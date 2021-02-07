from time import localtime, strftime
from flask import Flask, request, render_template, jsonify, redirect
from flask_socketio import SocketIO, join_room, leave_room, send
import sqlite3

import constants

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecret"
app.host = "localhost"
_socket_io = SocketIO(app)

ROOMS = ["common"]



# for getting data from members table
def select_element_members(column_name, value):
    # connect to database
    conn = sqlite3.connect('members.db')
    cur = conn.cursor()
    query_select_element_members = "SELECT * FROM members WHERE {}=\"{}\""
    query_select_element_members = query_select_element_members.format(column_name, value)
    print(query_select_element_members)
    result_select_element_members = cur.execute(query_select_element_members)
    result_select_element_members = list(result_select_element_members)
    return result_select_element_members


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # storing data in variables
        email = request.form.get("email")
        password = request.form.get("password")
        user_name = request.form.get("user_name")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        aadhar = request.form.get("aadhar")
        phone = request.form.get("phone")
        state = request.form.get("state")
        interest = request.form.get("interest")

        str_state_interest = "{}_{}"
        str_state_interest = str_state_interest.format(state, interest)
        if str_state_interest not in ROOMS:
            ROOMS.append(str_state_interest)
        # check if username or email exist
        # sql query to check if email already exists
        if select_element_members("email", email):
            return """email already exists"""



        if select_element_members("aadhar", aadhar):
            return """aadhar already exists"""
        # query for creating new account
        # connect to database
        conn = sqlite3.connect('members.db')
        cur = conn.cursor()
        query_signup = "INSERT INTO members(email, password, user_name, first_name, last_name, aadhar, phone, state, interest) VALUES(\"{}\", \"{}\", \"{}\", \"{}\",\"{}\", \"{}\", \"{}\", \"{}\", \"{}\")"
        query_signup = query_signup.format(email, password, user_name, first_name, last_name, aadhar, phone, state,
                                           interest)
        print(query_signup)
        cur.execute(query_signup)
        conn.commit()
        # collecting all the interests of person in a table with aadhar in the table name say "T"+aadhar_number
        conn = sqlite3.connect('interest.db')
        cur = conn.cursor()
        table_name = "T" + str(aadhar)
        # creating his interests table as he registers
        query_create_table = "CREATE TABLE {}(interest VARCHAR (255) NOT NULL)"
        query_create_table = query_create_table.format(table_name)
        print(query_create_table)
        cur.execute(query_create_table)
        # adding initial interest
        query_interest_table = "INSERT INTO {}(interest) VALUES(\"{}\")"
        query_interest_table = query_interest_table.format(table_name, interest)
        print(query_interest_table)
        cur.execute(query_interest_table)
        conn.commit()

        # creating group interests table as he registers
        conn = sqlite3.connect('group_interests.db')
        cur = conn.cursor()
        query_ct_group_interest = "CREATE TABLE IF NOT EXISTS {}(email VARCHAR (255) NOT NULL)"
        query_ct_group_interest = query_ct_group_interest.format(interest)
        print(query_ct_group_interest)
        cur.execute(query_ct_group_interest)
        # adding members to group of people with similar interests
        query_grp_interests = "INSERT INTO {}(email) VALUES(\"{}\")"
        query_grp_interests = query_grp_interests.format(interest, email)
        print(query_grp_interests)
        cur.execute(query_grp_interests)
        conn.commit()

        # creating group interests table as he registers
        conn = sqlite3.connect('group_interests_state.db')
        cur = conn.cursor()
        query_ct_group_interest_states = "CREATE TABLE IF NOT EXISTS {}(email VARCHAR (255) NOT NULL)"
        interest_state = "{}_{}"
        interest_state = interest_state.format(interest, state)
        query_ct_group_interest_states = query_ct_group_interest_states.format(interest_state)
        print(query_ct_group_interest_states)
        cur.execute(query_ct_group_interest_states)

        # adding members to group of people with similar interests
        query_grp_interests_state = "INSERT INTO {}(email) VALUES(\"{}\")"
        query_grp_interests_state = query_grp_interests_state.format(interest_state, email)
        print(query_grp_interests_state)
        cur.execute(query_grp_interests_state)
        conn.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if select_element_members("email", email):
            if password == select_element_members("email", email)[constants.list_index][constants.password_index]:
                redirect_link_to_chat = "/chat?email={}&userid={}"
                redirect_link_to_chat = redirect_link_to_chat.format(select_element_members("email", email)[constants.list_index][constants.email_index], select_element_members("email", email)[constants.list_index][constants.user_name_index])
                # state_interest = "{}_{}"
                # state_interest = state_interest.format(select_element_members("email", email)[constants.list_index][constants.state_index], select_element_members("email", email)[constants.list_index][constants.interest])
                # redirect_link_to_chat = redirect_link_to_chat.format(state_interest)

                return redirect(redirect_link_to_chat)
            else:
                return redirect("/login")


        else:
            return redirect("/login")
    return render_template("login.html")


@app.route("/chat", methods=["GET"])
def chats():
    if request.method == "GET":
        email = request.args.get("email")
        state_interest = "/chat/{}_{}?email={}&userid={}"
        data = list(select_element_members("email", email))
        print(data)
        print(state_interest)
        state_interest = state_interest.format(select_element_members("email", email)[constants.list_index][constants.state_index], select_element_members("email", email)[constants.list_index][constants.interest], select_element_members("email", email)[constants.list_index][constants.email_index], select_element_members("email", email)[constants.list_index][constants.user_name_index])

    return redirect(state_interest)




@app.route("/chat/<username>")
def chat(username):

    return render_template("chat.html")


@app.route("/profile/<username>")
def profile(username):

    email = select_element_members("user_name", username)[constants.list_index][constants.email_index]
    state = select_element_members("user_name", username)[constants.list_index][constants.state_index]
    interest = select_element_members("user_name", username)[constants.list_index][constants.interest]
    first_name = select_element_members("user_name", username)[constants.list_index][constants.first_name_index]
    last_name = select_element_members("user_name", username)[constants.list_index][constants.last_name_index]
    return render_template("profile.html", username=username, email=email, state=state, interest=interest, first_name=first_name, last_name=last_name)


def messageRecieved(methods=["GET", "POST"]):
    print("message was recieved")


@_socket_io.on("message")
def handleMessage(msg, methods=["GET", "POST"]):
    user_id = request.args.get("userid")
    _socket_io.emit("message", msg)
    return render_template("chat.html")




if __name__ == '__main__':
    _socket_io.run(app)
