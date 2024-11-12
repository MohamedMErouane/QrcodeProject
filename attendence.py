import datetime

import datetime


#fonction dyal store dyal l'attendence mn mora ma ghay tloga l user 
def store_attendance(user_id, session_id, db_connection): #had les arguments ghadi takhedhom mn return dyal fonction qr code 
   
    timestamp = datetime.datetime.now() # Get current timestamp when attendance is recorded

    cursor = db_connection.cursor()

    # Check if the user has already marked attendance for this session
    check_query = """
    SELECT COUNT(*) FROM attendance
    WHERE user_id = %s AND session_id = %s;
    """
    cursor.execute(check_query, (user_id, session_id))
    count = cursor.fetchone()[0]

    # If attendance not already marked, insert the attendance record
    if count == 0:
        insert_query = """
        INSERT INTO attendance (user_id, session_id, timestamp)
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (user_id, session_id, timestamp))
        db_connection.commit()  # Commit the transaction to the database
        return "Attendance stored in database."
    else:
        return "Attendance already stored."



#hadi 3la wed bach ghadi takhod l'attendence tged tkhdem biha ya bach t2aficher li 7ader f tableau binma bnadem kay scaner
#oula nged nkhdem biha ana bach nsift dk l mail f lekher d nhar 7int kat returni list 
def get_attendance_for_session(session_id, db_connection):
    cursor = db_connection.cursor()

    # Query to get all users who attended the session
    query = """
    SELECT u.username, a.timestamp
    FROM attendance a
    JOIN users u ON a.user_id = u.id
    WHERE a.session_id = %s
    ORDER BY a.timestamp ASC;
    """
    cursor.execute(query, (session_id,))
    result = cursor.fetchall()

    # Attendance information is stored in the database and fetched
    attendance_list = []
    for row in result:
        attendance_list.append({
            'username': row[0],    # User's name
            'timestamp': row[1]    # Timestamp of attendance
        })
    
    return attendance_list  # List of all attendees for the session


#hadi 3la wed l we9t bach tstora l'attendence 7int la dertiha f l qr ghadi i koun gher 7ader o ghayb db hadi ghadi tzid m3attel
def is_within_session_time(session_id, db_connection):
    cursor = db_connection.cursor()
    query = """
    SELECT start_time, end_time FROM sessions WHERE id = %s;
    """
    cursor.execute(query, (session_id,))
    session = cursor.fetchone()
    
    current_time = datetime.datetime.now()
    
    if session[0] <= current_time <= session[1]:
        return True
    else:
        return False
