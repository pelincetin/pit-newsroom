import os
import urllib.request
from flask import Flask, flash, g, request, redirect, url_for, render_template, jsonify
from flask_oidc import OpenIDConnect
from okta import UsersClient
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config["SECRET_KEY"] = ""
app.config["OIDC_ID_TOKEN_COOKIE_NAME"] = "oidc_token"
oidc = OpenIDConnect(app)
okta_client = UsersClient("", "")


current_id = 6
pictures = [{
		"Id": 1,
		"Name": "Pelin Cetin",
		"Caption": "Damage of the Flood",
		"Date": "2020-11-29",
		"Poster": "static/uploads/first.jpeg",
		"Description": "Over the course of the past number of years, flooding along the river and creeks that flow through Livingston Manor has inflicted serious property damage upon the many residences unfortunate enough to be in the path of the river valley's designated flood-plane. Still, the devastation caused over the course of the past few years by these floodwaters pales in comparison to the destruction amassed in just a few short hours by the work of large machines designed to destroy.",
		"Address": "Rock Ave",
		"City": "Livingston Manor",
		"Verified": "Verified",
		"Message": "",
		"VerificationDate": "2020-11-30",

	},
	{
		"Id": 2,
		"Name": "Will Cao",
		"Caption": "Heavy Rainfall",
		"Date": "2020-11-09",
		"Poster": "static/uploads/second.jpg",
		"Description": "Heavy rainfall during the evening of September 30th and the early morning hours of October 1st, estimated by some to total six inches of rain, drenched Livingston Manor and its surroundings, quickly filling the previously water-starved local streams and creeks with floodwaters. Considering the experiences from the recent flooding events at the Manor, this episode would probably be considered minor; unless, of course you are one of the residents still remaining in the flood prone areas.",
		"Address": "50 Main St",
		"City": "Livingston Manor",
		"Verified": "Verified",
		"Message": "",
		"VerificationDate": "2020-11-14",
	},
	{
		"Id": 3,
		"Name": "Aya Abdallah",
		"Caption": "The Drastic Change",
		"Date": "2020-11-29",
		"Poster": "static/uploads/third.jpeg",
		"Description": "Livingston Manor has long had a flare for the dramatic, the usual episodes being water related. Yesterday afternoon, however, added a new chapter in Manor misery; fire. In what sounded like the repeated percussion of cannons, the propane tanks alongside the Hoos building exploded, sending shock waves that broke windows and could be felt throughout the downtown section of the village as far away as Peck's Market.",
		"Address": "29 Main St",
		"City": "Livingston Manor",
		"Verified": "Verified",
		"Message": "",
		"VerificationDate": "2020-11-14"
	},
	{
		"Id": 4,
		"Name": "Amy Huang",
		"Caption": "Beaverkill Covered Bridge",
		"Date": "2020-11-19",
		"Poster": "static/uploads/fourth.jpeg",
		"Description": "While working on dismantling the approaches to the Beaverkill Covered Bridge during the winter of 2016-17, the bridge restoration work crew unearthed a cache of hides buried within the earthen ramp leading to the bridge’s eastern portal. These hides assumedly date back to the nineteenth century tannery of Wm. Ellswoth & Co. that was located at what is now the Beaverkill Campsite, next to the bridge.",
		"Address": "3 Ragin Rd",
		"City": "Roscoe",
		"Verified": "Verified",
		"Message": "",
		"VerificationDate": "2020-11-20"
	},
	{
		"Id": 5,
		"Name": "Pelin Cetin",
		"Caption": "The Arnold House",
		"Date": "2020-11-04",
		"Poster": "https://images.squarespace-cdn.com/content/v1/534d8565e4b0c7f5e4fcb4f7/1562030061043-ICZGG34BMCXHR40HHXGX/ke17ZwdGBToddI8pDm48kFyD7pzB8zoMIVY5aiUuFlp7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0jG2lbcDYBOeMi4OFSYem8DMb5PTLoEDdB05UqhYu-xbnSznFxIRsaAU-3g5IaylIg/foster-supply-hospitality-ARNOLD-2019-06-Conservatory-Food-Scott-Yoga-Exteriors-Lawrence-Braun-0001-LB2_2700.jpg",
		"Description": "The Arnold House is a lively Catskills getaway located on Shandelee Mountain, near the quaint town of Livingston Manor. With our Tavern, newly renovated Barn & Greenhouse, expansive grounds & hiking trails and access to the area's storied outdoor activities our mission is to treat our guests to the comfort and relaxation of casual country living.",
		"Address": "839 Shandelee Rd",
		"City": "Livingston Manor",
		"Verified": "Not Yet",
		"Message": "",
		"VerificationDate": "2020-11-24"
	},
	{
		"Id": 6,
		"Name": "Pelin Cetin",
		"Caption": "my cat",
		"Date": "2020-11-04",
		"Poster": "https://i.pinimg.com/736x/64/60/b8/6460b864d8cbecc1c58522e62ee37a38.jpg",
		"Description": "dis my cat",
		"Address": "NYC",
		"City": "New York",
		"Verified": "Rejected",
		"Message": "This is not historical.",
		"VerificationDate": "2020-11-24"
	},

]

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def before_request():
    if oidc.user_loggedin:
        g.user = okta_client.get_user(oidc.user_getfield("sub"))
    else:
        g.user = None

@app.route('/')
def main():
	return render_template('main.html', pictures=pictures)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/featured')
def featured():
	featured_pics = []
	for pic in pictures:
		if pic["Verified"] == "Verified":
			featured_pics.append(pic)

	return render_template('featured.html', pictures=featured_pics)

@app.route('/verify')
@oidc.require_login
def verify():
	verified_pics = []
	global pictures
	for pic in pictures:
		if pic["Verified"] == "Not Yet":
			verified_pics.append(pic)

	return render_template('verify.html', pictures=verified_pics)

@app.route('/upload')
@oidc.require_login
def upload_form():
	return render_template('upload.html')

@app.route('/my-uploads')
@oidc.require_login
def my_uploads():
	my_photos=[]
	name = g.user.profile.firstName + " " + g.user.profile.lastName
	for pic in pictures:
		if pic["Name"] == name:
			my_photos.append(pic)
	return render_template('my-uploads.html', pictures=my_photos)

@app.route('/uploaded', methods=['GET', 'POST'])
@oidc.require_login
def upload_image():
	global pictures
	global current_id

	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		poster=filename
		name=g.user.profile.firstName + " " + g.user.profile.lastName
		caption=request.form["caption"]
		description=request.form["description"]
		address=request.form["address"]
		city=request.form["city"]
		date=request.form["date"]

		new_picture_entry={
			"Id": current_id,
			"Name": name,
			"Caption": caption,
			"Date": date,
			"Poster": url_for('static', filename='uploads/' + filename),
			"Description": description,
			"Address": address,
			"City": city,
			"Verified": "Not Yet",
			"Message": "",
			"VerificationDate": None,
		}
		current_id += 1
		pictures.append(new_picture_entry)
		flash('Image was uploaded successfully')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)


@app.route('/delete_picture', methods=['GET', 'POST'])
def delete_picture():
	global pictures

	json_data = request.get_json()
	data_id = json_data["Id"]
	print(data_id)

	for pic in pictures:
		if int(pic["Id"]) == int(data_id):
			pictures.remove(pic)

	return jsonify(deleted=1)

@app.route('/verified', methods=['GET', 'POST'])
def verified():
	global pictures

	json_data = request.get_json()
	print(json_data)
	data_id = json_data["Id"]
	data_status = json_data["Status"]
	data_message = json_data["Message"]
	for pic in pictures:
		if int(pic["Id"]) == int(data_id):
			if data_status == "a":
				pic["Verified"] = "Verified"
			else:
				pic["Verified"] = "Rejected"
			pic["Message"] = data_message
	return jsonify(verified=1)

@app.route("/login")
@oidc.require_login
def login():
	print(g.user.profile)
	#print(g.user.profile.role)
	return redirect(url_for("upload_form"))


@app.route("/logout")
def logout():
    oidc.logout()
    return redirect(url_for("main"))


if __name__ == "__main__":
	app.run()
