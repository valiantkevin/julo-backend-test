from flask import Flask,request,jsonify,make_response,Blueprint
import sqlite3
import base64

walletBlueprint = Blueprint(name="wallet", import_name=__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def stringToBase64(string):
	string_bytes = string.encode("ascii")
	result_bytes = base64.b64encode(string_bytes)
	result = result_bytes.decode("ascii")
	return result

@walletBlueprint.route('/init', methods=['POST'])
def initialize():
	response = {}
	data = {}
	try:
		conn = get_db_connection()
		customer_xid = request.form['customer_xid']
		if customer_xid == "":
			response['status'] ="fail"
			data['customer_xid'] ="customer_xid is empty"
			response['data'] =data
			return make_response(jsonify(response),400)
		cursor = conn.execute("SELECT * FROM authorization WHERE customer_xid=?",(customer_xid,))
		if cursor.fetchone() is not None:
			response['status']="fail"
			data['customer_xid']="customer_xid already exist"
			response['data']=data
			return make_response(jsonify(response),400)
		token = stringToBase64(customer_xid)
		conn.execute("INSERT INTO authorization(customer_xid,token) VALUES (?,?)",(customer_xid,token))
		cursor = conn.execute("SELECT * FROM authorization WHERE customer_xid=?",(customer_xid,))
		customer_key = cursor.fetchone()[0]
		wallet_id = customer_xid[::-1]
		conn.execute("INSERT INTO wallets (wallet_id,customer_key) VALUES (?,?)",(customer_xid,customer_key))
		conn.commit()
		response['status'] = "success"
		data['token'] = token
		response['data'] = data
		return make_response(jsonify(response),201)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)

@walletBlueprint.route('/wallet', methods=['POST'])
def enableWallet():
	response = {}
	data = {}
	wallet ={}
	try:
		conn = get_db_connection()
		authorization = request.headers.get('Authorization')
		if authorization == "":
			response['status'] = "error"
			response['message'] ="authorization token should not be empty"
			return make_response(jsonify(response),401)
		token = authorization[6:]
		cursor = conn.execute("SELECT * FROM authorization WHERE token=?",(token,))
		row = cursor.fetchone()
		if row is None:
			response['status']="error"
			response['message']="authorization token not valid"
			return make_response(jsonify(response),401)
		customer_key = row[0]
		customer_xid = row[1]
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		if (row[3] == "enabled"):
			response['status'] = "fail"
			data['status'] = "wallet is already enabled"
			response['data'] = data
			return make_response(jsonify(response),400)
		conn.execute("UPDATE wallets SET status='enabled' WHERE customer_key=?",(customer_key,))
		conn.commit()
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		response['status'] = "success"
		wallet['id'] = row[1]
		wallet['owned_by'] = customer_xid
		wallet['status']='enabled'
		wallet['enabled_at']=row[4]
		wallet['balance']=row[5]
		data['wallet']=wallet
		response['data'] = data
		return make_response(jsonify(response),201)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)

@walletBlueprint.route('/wallet', methods=['PATCH'])
def disableWallet():
	response = {}
	data = {}
	wallet ={}
	try:
		conn = get_db_connection()
		authorization = request.headers.get('Authorization')
		is_disabled = request.form['is_disabled']
		if is_disabled == "" or is_disabled != "true":
			response['status'] = "error"
			response['message'] = "is_disabled should be true"
			return make_response(jsonify(response),400)
		if authorization == "":
			response['status'] = "error"
			response['message'] ="authorization token should not be empty"
			return make_response(jsonify(response),401)
		token = authorization[6:]
		cursor = conn.execute("SELECT * FROM authorization WHERE token=?",(token,))
		row = cursor.fetchone()
		if row is None:
			response['status']="error"
			response['message']="authorization token not valid"
			return make_response(jsonify(response),401)
		customer_key = row[0]
		customer_xid = row[1]
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		if (row[3] == "disabled"):
			response['status'] = "fail"
			data['status'] = "wallet is already disabled"
			response['data'] = data
			return make_response(jsonify(response),400)
		conn.execute("UPDATE wallets SET status='disabled' WHERE customer_key=?",(customer_key,))
		conn.commit()
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		response['status'] = "success"
		wallet['id'] = row[1]
		wallet['owned_by'] = customer_xid
		wallet['status']='disabled'
		wallet['disabled_at']=row[4]
		wallet['balance']=row[5]
		data['wallet']=wallet
		response['data'] = data
		return make_response(jsonify(response),200)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)

@walletBlueprint.route('/wallet', methods=['GET'])
def viewWallet():
	response = {}
	data = {}
	wallet ={}
	try:
		conn = get_db_connection()
		authorization = request.headers.get('Authorization')
		if authorization == "":
			response['status'] = "error"
			response['message'] ="authorization token should not be empty"
			return make_response(jsonify(response),401)
		token = authorization[6:]
		cursor = conn.execute("SELECT * FROM authorization WHERE token=?",(token,))
		row = cursor.fetchone()
		if row is None:
			response['status']="error"
			response['message']="authorization token not valid"
			return make_response(jsonify(response),401)
		customer_key = row[0]
		customer_xid = row[1]
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		if row[3]=='disabled':
			response['status']="error"
			response['message']="wallet is disabled"
			return make_response(jsonify(response),400)
		response['status'] = "success"
		wallet['id'] = row[1]
		wallet['owned_by'] = customer_xid
		wallet['status']=row[3]
		wallet['enabled_at']=row[4]
		wallet['balance']=row[5]
		data['wallet']=wallet
		response['data'] = data
		return make_response(jsonify(response),200)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)

@walletBlueprint.route('/deposit', methods=['POST'])
def depositWallet():
	response = {}
	data = {}
	deposit ={}
	try:
		conn = get_db_connection()
		amount = request.form['amount']
		reference_id = request.form['reference_id']
		if amount=="" or reference_id=="":
			response['status'] = "error"
			response['message'] ="amount and reference_id should not be empty"
			return make_response(jsonify(response),400)
		if int(amount)<=0:
			response['status'] = "error"
			response['message'] ="amount should be bigger than 0"
			return make_response(jsonify(response),400)
		authorization = request.headers.get('Authorization')
		if authorization == "":
			response['status'] = "error"
			response['message'] ="authorization token should not be empty"
			return make_response(jsonify(response),401)
		token = authorization[6:]
		cursor = conn.execute("SELECT * FROM authorization WHERE token=?",(token,))
		row = cursor.fetchone()
		if row is None:
			response['status']="error"
			response['message']="authorization token not valid"
			return make_response(jsonify(response),401)
		customer_key = row[0]
		customer_xid = row[1]
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		if row[3]=='disabled':
			response['status']="error"
			response['message']="wallet is disabled"
			return make_response(jsonify(response),400)
		balance = row[5]
		deposit_id = reference_id[::-1]
		conn.execute("INSERT INTO deposits (deposit_id,deposited_by,customer_key,amount,reference_id) VALUES (?,?,?,?)",(deposit_id,customer_xid,customer_key,amount,reference_id))
		balance += int(amount)
		conn.execute("UPDATE wallets SET balance=? WHERE customer_key=?",(balance,customer_key,))
		conn.commit()
		cursor = conn.execute("SELECT * FROM deposits WHERE reference_id=?",(reference_id,))
		row = cursor.fetchone()
		response['status'] = "success"
		deposit['id'] = row[0]
		deposit['deposited_by'] = customer_xid
		deposit['status'] = "success"
		deposit['deposited_at'] = row[3]
		deposit['amount'] = amount
		deposit['reference_id'] = reference_id
		data['deposit'] = deposit
		response['data'] = data
		return make_response(jsonify(response),201)
	except sqlite3.IntegrityError:
		response['status']="error"
		response['message']="reference_id already used"
		return make_response(jsonify(response),400)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)

@walletBlueprint.route('/withdrawal', methods=['POST'])
def withdrawWallet():
	response = {}
	data = {}
	withdrawal ={}
	try:
		conn = get_db_connection()
		amount = request.form['amount']
		reference_id = request.form['reference_id']
		if amount=="" or reference_id=="":
			response['status'] = "error"
			response['message'] ="amount and reference_id should not be empty"
			return make_response(jsonify(response),400)
		if int(amount)<=0 :
				response['status'] = "error"
				response['message'] ="amount should be bigger than 0"
				return make_response(jsonify(response),400)
		authorization = request.headers.get('Authorization')
		if authorization == "":
			response['status'] = "error"
			response['message'] ="authorization token should not be empty"
			return make_response(jsonify(response),401)
		token = authorization[6:]
		cursor = conn.execute("SELECT * FROM authorization WHERE token=?",(token,))
		row = cursor.fetchone()
		if row is None:
			response['status']="error"
			response['message']="authorization token not valid"
			return make_response(jsonify(response),401)
		customer_key = row[0]
		customer_xid = row[1]
		cursor = conn.execute("SELECT * FROM wallets WHERE customer_key=?",(customer_key,))
		row = cursor.fetchone()
		if row[3]=='disabled':
			response['status']="error"
			response['message']="wallet is disabled"
			return make_response(jsonify(response),400)
		balance = row[5]
		withdraw_id = reference_id[::-1]
		conn.execute("INSERT INTO withdrawals (withdraw_id,withdrawed_by,customer_key,amount,reference_id) VALUES (?,?,?,?)",(withdraw_id,customer_xid,customer_key,amount,reference_id))
		conn.commit()
		balance -= int(amount)
		conn.execute("UPDATE wallets SET balance=? WHERE customer_key=?",(balance,customer_key,))
		conn.commit()
		cursor = conn.execute("SELECT * FROM deposits WHERE reference_id=?",(reference_id,))
		row = cursor.fetchone()
		response['status'] = "success"
		withdrawal['id'] = row[0]
		withdrawal['deposited_by'] = customer_xid
		withdrawal['status'] = "success"
		withdrawal['deposited_at'] = row[3]
		withdrawal['amount'] = amount
		withdrawal['reference_id'] = reference_id
		data['withdrawal'] = withdrawal
		response['data'] = data
		return make_response(jsonify(response),201)
	except sqlite3.IntegrityError:
		response['status']="error"
		response['message']="reference_id already used"
		return make_response(jsonify(response),400)
	except:
		response['status']="error"
		response['message']="cannot communicate with the database"
		return make_response(jsonify(response),500)