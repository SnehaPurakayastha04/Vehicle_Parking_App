from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import extract, func
import json
app=Flask(__name__)
app.secret_key='your_super_secret_key_here'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
db=SQLAlchemy()#initialization
db.init_app(app)
app.app_context().push()
from flask_migrate import Migrate
migrate=Migrate(app,db)

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(100), nullable=False)
    lname=db.Column(db.String(100), nullable=False)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password=db.Column(db.String(120), nullable=False)
    is_admin=db.Column(db.Boolean, default=False)

class ParkingLot(db.Model):
    __tablename__='parking_lot'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    address=db.Column(db.String(50), nullable=False)
    pincode=db.Column(db.Integer, nullable= False)
    price_per_hour=db.Column(db.Float,nullable=False)
    max_spots=db.Column(db.Integer, nullable=False)
    spots=db.relationship('ParkingSpot',backref='lot')

class ParkingSpot(db.Model):
    __tablename__='parking_spot'
    id=db.Column(db.Integer, primary_key=True)
    lot_id=db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status=db.Column(db.String(1),default='A')#A=Available and O=Occupied

class Reservation(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    spot_id=db.Column(db.Integer,db.ForeignKey('parking_spot.id'), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    start_time=db.Column(db.DateTime,nullable=False)
    end_time=db.Column(db.DateTime)
    cost=db.Column(db.Float)
    vehicle_number=db.Column(db.String(20))
    duration=db.Column(db.Float)
    

db.create_all()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        user_name=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=user_name).first()
        if user:
            if user.password==password:
                username=user.username
                first_name=user.fname
                return redirect(url_for('dashboard', user_name=username, first_name=first_name))
            else:
                flash("Password Incorrect!!!","danger")
                return redirect(url_for('login'))
        else:
            flash("Account does not exist. Please register first","danger")
            return redirect('/register')
   
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method=='POST':
        user_name=request.form.get('username')
        password=request.form.get('password')
        first_name=request.form.get('fname')
        last_name=request.form.get('lname')
        user_exists=User.query.filter_by(username=user_name).first()
        if user_exists:
            return render_template('register.html', error="Username already registered")
        else:
            new_user=User(username=user_name,password=password,fname=first_name, lname=last_name)
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created Successfully","success")
            return redirect('/login')
        
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='GET':
        return render_template('admin_login.html')
    else:
        username=request.form.get('username')
        password=request.form.get('password')

        if username=='admin' and password=='passadmin':
            return redirect(url_for('admin_dashboard', user_name=username))
        else:
            flash("Invalid Admin Credentials",'danger')
            return redirect(url_for('admin_login'))
        

@app.route('/dashboard/<string:user_name>')
def dashboard(user_name):
    user=User.query.filter_by(username=user_name).first()
    if not user:
        return "User not Found"
    active_reservation=Reservation.query.filter(Reservation.user_id==user.id, Reservation.end_time.is_(None)).all()

    #Past reservations
    past_reservations=Reservation.query.filter(Reservation.user_id==user.id,Reservation.end_time.isnot(None)).order_by(Reservation.start_time.desc()).all()
    first_name=user.fname
    print(first_name)
    print(user)

    monthly_counts=[0]*12
    for reservation in past_reservations:
        if reservation.start_time:
            month=reservation.start_time.month-1
            monthly_counts[month]+=1
        
    monthly_counts_json=json.dumps(monthly_counts)
    print("Sending JSON:", monthly_counts_json) 

        
    return render_template('dashboard.html', monthly_counts=monthly_counts_json, user_name=user_name,reservations=active_reservation,first_name=first_name,past_reservations=past_reservations)

@app.route('/view-lots/<string:username>')
def view_lots(username):
    lots=ParkingLot.query.all()
    lot_data=[]
    for lot in lots:
        available_spots=sum(1 for spot in lot.spots if spot.status=='A')
        lot_data.append({'id':lot.id,'name':lot.name,'address':lot.address,'max_spots':lot.max_spots, 'available_spots':available_spots})

    return render_template('view_lots.html', lots=lot_data, username=username)

@app.route('/book_lot/<int:lot_id>/<string:username>', methods=['GET','POST'])
def book_lot(lot_id, username):
    user=User.query.filter_by(username=username).first()
    lot=ParkingLot.query.get(lot_id)
    vehicle_number=request.form.get('vehicle_number')
    if not user:
        return "User not found"
    elif not lot:
        return "Lot not found"
    existing_reservation=Reservation.query.join(ParkingSpot).filter(Reservation.user_id==user.id, Reservation.end_time==None, ParkingSpot.status=='O').first()
    if existing_reservation:
        flash("You already have an active reservation.","warning")
        return redirect(url_for('dashboard', user_name=username))
    for spot in lot.spots:
        if spot.status=="A":
            spot.status="O"
            reservation=Reservation(spot_id=spot.id,
                user_id=user.id,
                start_time=datetime.now(),
                cost=0,
                vehicle_number=vehicle_number)
            db.session.add(reservation)
            db.session.commit()
            break
    return redirect(url_for('dashboard', user_name=username))
    

@app.route('/release_spot/<int:reservation_id>/<string:username>', methods=['POST'])
def release_spot(reservation_id,username):
    reservation=Reservation.query.get(reservation_id)
    if not reservation:
        return "Reservation Not Found"
    spot=ParkingSpot.query.get(reservation.spot_id)
    lot=ParkingLot.query.get(spot.lot_id)
    reservation.end_time=datetime.now()
    duration_in_hours=(reservation.end_time-reservation.start_time).total_seconds()/3600
    reservation.duration=round(duration_in_hours,2)
    reservation.cost=round(reservation.duration*lot.price_per_hour, 2)
    spot.status="A"
    db.session.add(reservation)
    db.session.add(spot)
    db.session.commit()
    flash(f"Spot Released. Total Cost:{reservation.cost}","success")
    return redirect(url_for('dashboard',user_name=username))

@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if request.method=='GET':
        return render_template('add_lot.html')
    if request.method=='POST':
        name=request.form.get('lot_name')
        address=request.form.get('lot_address')
        pincode=request.form.get('lot_pincode')
        price=float(request.form.get('price'))
        max_spots=int(request.form.get('max_spots'))

        new_lot=ParkingLot(name=name, address=address, price_per_hour=price, max_spots=max_spots, pincode=pincode)
        db.session.add(new_lot)
        db.session.commit()

        #Auto creation of parking spots
        for _ in range(max_spots):
            spot=ParkingSpot(lot_id=new_lot.id,status='A')
            db.session.add(spot)
        db.session.commit()
        flash("Parking Lot added successfully!!!!","success")
        return redirect(url_for('admin_dashboard', user_name='admin'))
    
@app.route('/admin_dashboard/<string:user_name>')
def admin_dashboard(user_name):
    # lots=ParkingLot.query.all()#Fetching all the lots 
    # occupied_spots=db.session.query(ParkingSpot,Reservation,User).join(Reservation, ParkingSpot.id==Reservation.spot_id)\
    # .join(User, Reservation.user_id==User.id).filter(ParkingSpot.status=='O').all()
    # now=datetime.now()
    
    return render_template('admin_dashboard.html',user_name=user_name)
    
@app.route('/edit_lot/<int:lot_id>', methods=['GET','POST'])
def edit_lot(lot_id):
    lot=ParkingLot.query.get(lot_id)
    if request.method=='GET':
        return render_template('edit_lot.html',lot=lot)
    if request.method=='POST':
        lot.name=request.form.get('name')
        lot.address=request.form.get('address')
        lot.price_per_hour=request.form.get('price_per_hour')
        new_max_spots=int(request.form.get('max_spots'))

        current_spots=len(lot.spots)
        occupied_spots=len([spot for spot in lot.spots if spot.status=='O'])

        if new_max_spots < occupied_spots:
           flash("Operation not permitted: Occupied spots exceed the new spot count.","danger")
           return redirect(url_for('edit_lot',lot_id=lot_id))
        if new_max_spots > current_spots: #Addition of extra spots
            for _ in range(new_max_spots-current_spots):
                new_spot=ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif new_max_spots < current_spots: #Deletion of extra spots
            removable=[spot for spot in lot.spots if spot.status=='A']#The number of spots available that can be removed
            to_remove=current_spots-new_max_spots#Number of spots that is to be reduced
            if len(removable) < to_remove:
                flash("Reduction denied: the number of free spots is insufficient","danger")
                return redirect(url_for('edit_lot',lot_id=lot_id))
            for spot in removable[:to_remove]:
                db.session.delete(spot)

        lot.max_spots=new_max_spots
        db.session.commit()
        return redirect('/admin_dashboard/admin')

@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot=ParkingLot.query.get(lot_id)
    if any(spot.status=="O" for spot in lot.spots):
        flash("Deletion failed: Some parking spots in this lot are currently occupied.","danger")
        return redirect(url_for('admin_dashboard',user_name='admin'))
    
    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully","success")
    return redirect(url_for('parking_lot_details'))

@app.route('/view_users')
def view_users():
    users=User.query.filter_by(is_admin=False).all()
    return render_template('view_users.html',users=users)

@app.route('/parking_lot_details')
def parking_lot_details():
    lots=ParkingLot.query.all()
    lot_data = []
    
    for lot in lots:
        spots_info = []
        for spot in lot.spots:
            if spot.status == "O":
                reservation = Reservation.query.filter_by(spot_id=spot.id, end_time=None).first()
                if reservation:
                    user = User.query.get(reservation.user_id)
                    spots_info.append({
                        "number": spot.id,
                        "status": "Occupied",
                        "vehicle": reservation.vehicle_number,
                        "user": user.username
                    })
            else:
                spots_info.append({
                    "number": spot.id,
                    "status": "Available",
                    "vehicle": None,
                    "user": None
                })
        lot_data.append({"lot": lot, "spots": spots_info})

    return render_template('parking_lot_detail.html',lots=lots, lot_data=lot_data)


@app.route('/admin/occupied_spots')
def occupied_spots():
    occupied_spots=db.session.query(ParkingSpot,Reservation,User).join(Reservation, ParkingSpot.id==Reservation.spot_id)\
    .join(User, Reservation.user_id==User.id).filter(ParkingSpot.status=='O', Reservation.end_time==None).all()
    now=datetime.now()
    updated_details=[]
    for spot, reservation, user in occupied_spots:
        lot=ParkingLot.query.get(spot.lot_id)
        duration_hours=(now-reservation.start_time).total_seconds()/3600
        current_cost=round(duration_hours*lot.price_per_hour, 2)
        updated_details.append((spot, reservation, user, duration_hours, current_cost))
    return render_template('occupied_spots.html',occupied_details=updated_details,now=now)

@app.route('/admin/summary_chart')
def admin_summary_chart():
    reservations_data = (db.session.query(extract('month', Reservation.start_time).label('month'),func.count(Reservation.id).label('count') ).group_by('month').order_by('month').all())
    revenue_data = (db.session.query(extract('month', Reservation.start_time).label('month'), func.sum(Reservation.cost).label('revenue')).group_by('month').order_by('month').all())

    reservations_count = [0] * 12
    revenue_count = [0] * 12

    for m, c in reservations_data:
        reservations_count[int(m) - 1] = c


    for m, rev in revenue_data:
        revenue_count[int(m) - 1] = float(rev or 0)


    return render_template('admin_summary_chart.html',reservations_count=reservations_count,revenue_count=revenue_count)


    

def create_auto_admin():
    if_exists=User.query.filter_by(is_admin=True).first()
    if not if_exists:
        admin=User(fname='Sneha',lname='Purakayastha',username='admin', password='passadmin',is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin got created")
    else:
        print("Admin already exists")

    

if __name__ == '__main__':
    create_auto_admin()
    app.run(debug=True)