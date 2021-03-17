#services/users/manage.py 

import unittest
from flask import Blueprint, jsonify, request, render_template, current_app, flash
from flask.cli import FlaskGroup
# from project.app import create_app, db, mongoEngine, pyMongo
from project.app import create_app, db, mongoEngine, celery
from project.api.models import User, Application, Application_M, User_M, Certificate_M, Video_M, Course_M, DynamoDBClient, DynamoDB

import sys
import json
import os

import bson

from bson.objectid import ObjectId


from datetime import datetime

from mongoengine.queryset.visitor import Q

from botocore.exceptions import ClientError
import decimal
from boto3.dynamodb.conditions import Key, Attr

from jose import jwt

import boto3
# https://stackoverflow.com/questions/51242939/query-an-embeddeddocumentfieldlist-by-mongoengine-use-or-operate




app = create_app()
cli = FlaskGroup(create_app=create_app)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)



# @cli.command()
# def createdynamodbtable():
# 	dynamodb_client = DynamoDBClient().get_client()
# 	dynamodb = DynamoDB(dynamodb_client)
# 	table_name = 'itpacsusers'
	
# 	#define attributes
# 	attribute_definitions = [
# 			{
# 	            'AttributeName': 'username',
# 	            'AttributeType': 'S'
#             }
#             ]

# 	key_schema = [
# 					{'AttributeName': 'username',
# 					 'KeyType': 'HASH' 
# 					 }
# 				]

# 	iops = {
# 	        'ReadCapacityUnits': 10,
# 	        'WriteCapacityUnits': 10
# 	    	}

# 	dynamodb_create_table_response = dynamodb.create_table(table_name, attribute_definitions, key_schema, iops)
# 	print(f'created dynamodb table named {table_name}: {str(dynamodb_create_table_response)}')




@cli.command()
def recreatedb():

	db.drop_all()
	db.create_all()
	db.session.commit()


#Batch put items
@cli.command()
def seedcertsindynamodb():
	certs = getcerts()
	print(certs[0])
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	#To delete existing table and create a fresh one
	table = dynamodb.Table('itpacsdata')

	for eachCert in certs:
		partition_k = f"APPLICATION-{eachCert['Code']}"
		sort_k = f"APPLICATION-{eachCert['domain']}-{eachCert['framework']}"
		domain = eachCert['domain']
		framework = eachCert['framework']
		sub_domain = eachCert['sub_domain']
		certificate_title = eachCert['title']
		created = int(datetime.today().timestamp())
		certification_owner = 'ITPACS'
		data = 'APPLICATION'

		print(f"Adding certification:, {certificate_title}")

		table.put_item(
			Item={
			'partition_k': partition_k,
			'sort_k': sort_k,
			'domain': domain,
			'framework': framework,
			'sub_domain': sub_domain,
			'certificate_title': certificate_title,
			'created': created,
			'certification_owner': certification_owner,
			'data': data
			}
			)

@cli.command()
def additpacscertificateachieved():
	

	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])
	table = dynamodb.Table('itpacsdata')

	certificateObtained = {'Code': 6,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Machine Learning Basics'}

	emailsOfUsers = ['v1@ikompass.com',
					 'v2@ikompass.com',
					 'v3@ikompass.com'
					]

	partition_k = f"APPLICATION-{certificateObtained['Code']}"

	for eachEmail in emailsOfUsers:
		sort_k = f"APPLICATION {eachEmail}"
		print(f"Adding New Item:, partition_k:{partition_k}, sort_k :{sort_k }")
		
		table.put_item(
			Item={
			'partition_k': partition_k,
			'sort_k': sort_k,
			'certificate_title': certificateObtained['title'],
			'obtained' : datetime.utcnow().isoformat(),
			'sub_domain': certificateObtained['sub_domain'],
			'domain': certificateObtained["domain"],
			'certification_owner': "ITPACS",
			'data': 'APPLICATION',
			'framework': certificateObtained['framework'],
			'status': 'achieved',
			'verification': 'Verified',
			'country': 'Singapore'
			}
			)



@cli.command()
def deleteitpacscertificateachieved():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	emailsOfUsers = ['v1@ikompass.com',
					 'v2@ikompass.com',
					 'v3@ikompass.com'
					]

	table = dynamodb.Table('itpacsdata')
	
	for eachEmail in emailsOfUsers:
		print(f"Deleting: partition_k: APPLICATION-6, sort_k: APPLICATION {eachEmail}")
		response = table.delete_item(
				Key={
				'partition_k': f"APPLICATION-6",
				'sort_k': f"APPLICATION {eachEmail}"
				}
				)


#Batch delete items
@cli.command()
def deletecertsindynamodb():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	certs = getcerts()

	table = dynamodb.Table('itpacsdata')
	
	for eachCert in certs:
		print(f"Deleting: {eachCert['title']}")
		response = table.delete_item(
				Key={
				'partition_k': f"APPLICATION-{eachCert['Code']}",
				'sort_k': "APPLICATION-{eachCert['domain']}-{eachCert['framework']}"
				}
				)



#Create a GSI. You can create GSI even after initial table creation
@cli.command()
def createglobalsecondaryindex1():
	dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	

	response = dynamodb.update_table(
		TableName='itpacsdata',
		AttributeDefinitions=[
            {
                "AttributeName": "sort_k",
                "AttributeType": "S"
            },
        ],
		GlobalSecondaryIndexUpdates=[
			{
				'Create': {
				'IndexName': 'CertsByDomainFramework',
				'KeySchema': [
					{
						'AttributeName': 'sort_k',
						'KeyType': 'HASH'
					}
				],
				'Projection':{
					'ProjectionType': 'ALL'
				},
				'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
				}

			}
		}
		]
		)

#Create a GSI. You can create GSI even after initial table creation
@cli.command()
def createglobalsecondaryindex2():
	dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])
	

	response = dynamodb.update_table(
		TableName='itpacsdata',
		AttributeDefinitions=[
            {
                "AttributeName": "data",
                "AttributeType": "S"
            },
        ],
		GlobalSecondaryIndexUpdates=[
			{
				'Create': {
				'IndexName': 'GSI_2',
				'KeySchema': [
					{
						'AttributeName': 'data',
						'KeyType': 'HASH'
					}
				],
				'Projection':{
					'ProjectionType': 'ALL'
				},
				'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
				}

			}
		}
		]
		)

@cli.command()
def thirdsecondaryindexcreate():
	dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])
	

	response = dynamodb.update_table(
		TableName='itpacsdata',
		AttributeDefinitions=[
            {
                "AttributeName": "data2",
                "AttributeType": "S"
            },
        ],
		GlobalSecondaryIndexUpdates=[
			{
				'Create': {
				'IndexName': 'GSI_3',
				'KeySchema': [
					{
						'AttributeName': 'data2',
						'KeyType': 'HASH'
					}
				],
				'Projection':{
					'ProjectionType': 'ALL'
				},
				'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
				}

			}
		}
		]
		)


# @cli.command()
# def createglobalsecondaryindex3():
# 	dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1', 
# 		endpoint_url="http://dynamodb:8000", 
# 		aws_access_key_id=current_app.config['S3_KEY'],
# 		aws_secret_access_key=current_app.config['S3_SECRET'])
	

# 	response = dynamodb.update_table(
# 		TableName='itpacsdata',
# 		AttributeDefinitions=[
#             {
#                 "AttributeName": "data2",
#                 "AttributeType": "S"
#             },
#         ],
# 		GlobalSecondaryIndexUpdates=[
# 			{
# 				'Create': {
# 				'IndexName': 'GSI_3',
# 				'KeySchema': [
# 					{
# 						'AttributeName': 'data2',
# 						'KeyType': 'HASH'
# 					}
# 				],
# 				'Projection':{
# 					'ProjectionType': 'ALL'
# 				},
# 				'ProvisionedThroughput': {
#                     'ReadCapacityUnits': 5,
#                     'WriteCapacityUnits': 5
# 				}

# 			}
# 		}
# 		]
# 		)


#Query GSI
@cli.command()
def queryglobalsecondaryindex():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(
		IndexName='CertsByDomainFramework',
		KeyConditionExpression=Key('sort_k').eq('APPLICATION-Web Development-Associate')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

#Query for all certificates of user-123
@cli.command()
def queryglobalsecondaryindexcertsofuser():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(
		IndexName='CertsByDomainFramework',
		KeyConditionExpression=Key('sort_k').eq('USER-de055954-9c7f-4e8d-8ff2-78acdccc8cb0')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	print(json.dumps(response['Items']))



@cli.command()
def queryglobalsecondaryindex2():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(
		IndexName='GSI_2',
		KeyConditionExpression=Key('email').eq("m6@ikompass.com")
		)
	print("The query returned the following items:")
	items = response.get('Items')
	print(items)
	# for item in response['Items']:
	# 	print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	# print(json.dumps(response['Items']))





@cli.command()
def queryglobalsecondaryindexcoursesofteacher():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(
		IndexName='CertsByDomainFramework',
		KeyConditionExpression=Key('sort_k').eq("COURSE TEACHER USER-1defe6cb-c7c3-48c8-b715-96f398e1ac84")
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	print(json.dumps(response['Items']))


#Query for all users of Application 1
@cli.command()
def queryusersofcertfrommaintable():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(		
		KeyConditionExpression=Key('partition_k').eq('APPLICATION-1') & Key('sort_k').begins_with('APPLICATION USER')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	print(json.dumps(response['Items']))

@cli.command()
def querystudentsofcoursefrommaintable():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(		
		KeyConditionExpression=Key('partition_k').eq('COURSE-1569662377') & Key('sort_k').begins_with('COURSE STUDENT')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	# print(json.dumps(response['Items']))




#Query for all items of Application 1. Seach by partitiion key on main table
@cli.command()
def queryaspecificapplication():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(

		KeyConditionExpression=Key('partition_k').eq('APPLICATION-1')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	# print(json.dumps(response['Items']))


#Query for all users of Application 1
@cli.command()
def queryallusers():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])


	table = dynamodb.Table('itpacsdata')
	response = table.query(
		IndexName='CertsByDomainFramework',		
		KeyConditionExpression=Key('sort_k').eq('USER')
		)
	print("The query returned the following items:")
	for item in response['Items']:
		print(item)

	# [print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]
	# print(json.dumps(response['Items']))



@cli.command()
def deletedynamotable():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	#To delete existing table and create a fresh one
	table = dynamodb.Table('itpacsdata')
	table.delete()



@cli.command()
def createdynamotable():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	table = dynamodb.create_table(
		TableName='itpacsdata',
		KeySchema=[
			{
				'AttributeName': 'partition_k', # example #From Cognito username
				'KeyType': 'HASH' #Partition key
			},
			{
				'AttributeName': 'sort_k', # Sort Key
				'KeyType': 'RANGE' #Sort key
			},

		],
		AttributeDefinitions=[
        {
            'AttributeName': 'partition_k',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'sort_k',
            'AttributeType': 'S'
        }        
        
	    ],
	    ProvisionedThroughput={
	        'ReadCapacityUnits': 10,
	        'WriteCapacityUnits': 10
	    	}
		)

	print("Table Status", table.table_status)






@cli.command()
def testingmongo():
	dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1', 
		endpoint_url="http://dynamodb:8000", 
		aws_access_key_id=current_app.config['S3_KEY'],
		aws_secret_access_key=current_app.config['S3_SECRET'])

	#To delete existing table and create a fresh one
	table = dynamodb.Table('MY_DATA')
	table.delete()

	
	#Create a table
	table = dynamodb.create_table(
		TableName='MY_DATA',
		KeySchema=[
			{
				'AttributeName': 'userid', # example #101
				'KeyType': 'HASH' #Partition key
			},
			{
				'AttributeName': 'FNAME_LNAME', #example First_name Last_Name columns
				'KeyType': 'RANGE' #Sort Key. #Assunung owner firstname and lastname
			}
		],
		AttributeDefinitions=[
        {
            'AttributeName': 'userid',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'FNAME_LNAME',
            'AttributeType': 'S'
        }
        
	    ],
	    ProvisionedThroughput={
	        'ReadCapacityUnits': 10,
	        'WriteCapacityUnits': 10
	    	}
		)

	print("Table Status", table.table_status)

	#Add an item
	table.put_item(
			Item={
			'userid': 1,
			'FNAME_LNAME': 'Roshan Prakash',
			'info': {
					'role': 'Student',
					'company': 'iKompass'
				}
			}
		)

	table.put_item(
			Item={
			'userid': 2,
			'FNAME_LNAME': 'Babu P',
			'info': {
					'role': 'Teacher',
					'company': 'Sugi',
					'aboutme': 'Programmer',
					'courses': [{
					'course_title': 'Java',
					'students': ['Roshan Prakash', 'Surya']
					}, {'course_title': 'Python'}]
				}
			}
		)

	#Get single item
	try:
		response = table.get_item(
			Key={
			'userid': 1,
			'FNAME_LNAME': 'Roshan Prakash'
				}
			)
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		item = response['Item']
		print("Get Item succeeded")
		print(json.dumps(item, indent=4, cls=DecimalEncoder))


	#Query
	response = table.query(
		KeyConditionExpression=Key('userid').eq(2)
		)

	[print(json.dumps(x, indent=4, cls=DecimalEncoder)) for x in response['Items']]


	# pass


	# #Code to delete a student from a course
	# user_m = User_M.objects(id=4).get()
	# # course_id1=request.get_json().get('course_id1')
	# course_id1='5d4fe62a9a70c0000c138467'
	# # student_id =request.get_json().get('student_id')
	# student_id ='12'
	
	# a_course = user_m.courses.filter(id1=ObjectId(course_id1)).first()
	# print(a_course.to_json())
	
	# for eachStudent in a_course.students:		
	# 	if eachStudent.id == int(student_id):
	# 		a_course.students.remove(eachStudent)

	# print(type(a_course.students))
	# print(a_course.students)

	# user_m.save()
	# print(a_course.to_json())

	# #Remove course in all students who have enrolled
	# for eachStudent in a_course.students:
	# 	if eachStudent.id != user_m.id:
	# 		a_course = eachStudent.courses.filter(id1=ObjectId(course_id1)).first()
	# 		if eachStudent in a_course.students:
	# 			a_course.students.remove(eachStudent)
	# 			eachStudent.save()
	# 		# if int(student_id) in a_course.students:
	# 		# 	a_course.students.remove(int(student_id))
	# 		# 	eachStudent.save()



	# response_object = {
	# 					'status':'Success',
	# 					'message': 'Deleted Student'
	# 				}
	
	# return jsonify(response_object), 201








	#Code to get list of students for a course
	# course_id1 = '5d4fe62a9a70c0000c138467'
	# 	#Course id is guaranteed

	# user_m = User_M.objects(id=4).first()
	# a_course = user_m.courses.filter(id1=ObjectId(course_id1)).first()

	# students = a_course.students
	# student_details = [{'firstname': student.firstname, 
	# 				'lastname': student.lastname,
	# 				'profile_thumbnail_url': student.profile_thumbnail_url,
	# 				'id': student.id
	# 				} for student in students if student.firstname != None]	
	
	# print(student_details)



	
	# #Code to add students to a course
	# course_id1 = '5d4ed484a5b3ef000ec77ea4'
	# 	#Course id is guaranteed

	# user_m = User_M.objects(id=4).first()
	# a_course = user_m.courses.filter(id1=ObjectId(course_id1)).first()
	

	# student_emails = ['rosh1@ikompass.com', 'rosh2@ikompass.com', 'rosh3@ikompass.com', 'rosh4@ikompass.com', 'jason@ikompass.com']
	# 	#List of emails to be added to a course (collected from form)

	# users = User_M.objects.filter(email__in=student_emails)
	# print('Existing users in ITPACS:')
	# [print(x) for x in list(users)]
	# 	#itpacs registered users. Search mongodb to check if users with emails exists


	# emails_not_existing_users = set(student_emails) - set(list([x.email for x in users]))
	# print('Not existing in ITPACS')
	# print(list(emails_not_existing_users))


	# 	#Add ITPACS registered uses to the students list of a course
	# [a_course.students.append(eachUser) for eachUser in users if eachUser not in a_course.students]
	



	# if emails_not_existing_users:
	# 	for eachUserEMail in emails_not_existing_users:
	# 			#Create a user in postgres
	# 		new_user = User(email=eachUserEMail)
	# 		new_user.email_sent = True
	# 		db.session.add(new_user)
	# 		db.session.commit()
	# 		print(new_user)
	# 			#Create a user in mongodb
	# 		new_userM = User_M(id=new_user.id, email=new_user.email)
			
	# 			#Send an email using celery
	# 		body = render_template('emailToSendToNewAddedStudents.txt', 
	# 									register_url='https://www.itpacs.org', 
	# 									email=new_user.email,
	# 									course=a_course.course_title,
	# 									trainer=f'{user_m.firstname} {user_m.lastname}')

	# 		subject = f'ITPACS. {user_m.firstname} added you to the course - {a_course.course_title}'
	# 		celery.send_task('send_async_email', args=[new_user.email, body, subject])
	# 		new_userM.email_sent = True
			
	# 			#Save newly created user in mongodb
	# 		new_userM.save()
	# 			#Add the newly created user to the students list
	# 		a_course.students.append(new_userM)


	# user_m.save()

	# 	#Update the course inside each student
	# print('Printing eachStudent')
	# for eachStudent in a_course.students:
	# 	if eachStudent.id != user_m.id:		
	# 		if a_course not in eachStudent.courses:
	# 			eachStudent.courses.append(a_course)
	# 			eachStudent.save()
	# 			print(eachStudent.to_json())

	# #End of code to add students to a course

	





	#Show list of videos in a course
	# course_id1 = '5d4442991b8ba3000c0feeb6'
	# response_object = {
	# 					'status': 'Success',
	# 					'message': 'No courses found',						
	# 				}

	# user_m = User_M.objects(id=int(4)).first()	
	# a_course = user_m.courses.filter(id1=ObjectId(course_id1)).first()
	# videos = json.loads(a_course.to_json())['videos']

	# v_list_comp = a_course.videos.filter(status='COMPLETE')

	# print(v_list_comp)
	
	# if videos:
	# 	response_object['message'] = f'Found {len(videos)} videos'
	# 	response_object['videos'] = videos

	# print(response_object)
	# # return jsonify(response_object), 201
	#End of Show list of videos in a course






	

	#Delete a video
	# url = 'https://itpacsdatalakevideos2019compressed.s3-ap-southeast-1.amazonaws.com/assets/184a6cc311df4801a3019adb91981a82/HLS/184a6cc311df4801a3019adb91981a82.m3u8'
	# file_name = url.split('/')[4]

	# user_m = User_M.objects(id=int(4)).get()
	# a_course = user_m.courses.filter(id1=ObjectId("5d387ae718fdb400840348d4")).first()
	
	# for video in a_course.videos:
	# 	if video.id1 == ObjectId("5d387d6718fdb400bc98070d"):
	# 		a_course.videos.remove(video)

	# user_m.save()

	# prefix = f"assets/{file_name}"
	# print(prefix)

	# client = boto3.client('s3', region_name='ap-southeast-1',
	# 	aws_access_key_id=current_app.config['S3_KEY'],
	# 	aws_secret_access_key=current_app.config['S3_SECRET'])


	# client.put_bucket_lifecycle_configuration(
 #    Bucket='itpacsdatalakevideos2019compressed',
 #    LifecycleConfiguration={
 #        'Rules':[
 #            {
 #                "Expiration": {                    
 #                    "Days": 1                    
 #                }, 
 #                "Status": "Enabled",
 #                "Filter": {
 #                    "Prefix": prefix                  
 #                    }
                 
 #                }
                
            
 #        		]
 #        	}
 #        )
	#End of Delete a video
	




	#Get all videos of a course
		#Course id is guaranteed
	# post_data = {
	# 	'course_id1': '5d2ee6b944edd300152c2273'}

	# response_object = {
	# 					'status': 'Success',
	# 					'message': 'No courses found',						
	# 				}

	# user_m = User_M.objects(id=int(4)).first()	
	# a_course = user_m.courses.filter(id1=ObjectId(post_data['course_id1'])).first()
	# videos = json.loads(a_course.to_json())['videos']
	
	# if videos:
	# 	response_object['message'] = f'Found {len(videos)} videos'
	# 	response_object['videos'] = videos

	# print(videos)

	
	# #Add a or update video to a course
	# 	#Course id guaranteed
	# post_data = {
	# 	'video_title': 'Cyber Security Foundation',
	# 	'video_description': 'All about Cyber security',
	# 	"video_url": 'http://www.itpacs.org',
	# 	"video_thumbnail_url": 'http://www.itpacs.org',
	# 	'course_id1': '5d2ee6b944edd300152c2273',
	# 	"id1": '5d2ef1a82add090001c8f75d'
	# }

	# user_m = User_M.objects(id=4).get()
	# a_course = user_m.courses.filter(id1=ObjectId(post_data['course_id1'])).first()

	# if 'id1' not in post_data.keys():
	# 	a_video = Video_M()
	# 	for k, v in post_data.items():
	# 		if k != 'course_id1':
	# 			a_video[k] = v
	# 	a_course.videos.create(**json.loads(a_video.to_json()))
	# else:
	# 	if not post_data['id1']:
	# 		a_video = Video_M()
	# 		for k, v in post_data.items():
	# 			if k != 'course_id1':
	# 				a_video[k] = v
	# 		a_course.videos.create(**json.loads(a_video.to_json()))
	# 	else:
	# 		a_video = a_course.videos.filter(id1=ObjectId(post_data['id1'])).first()
	# 		for k, v in post_data.items():
	# 			if k != 'course_id1':
	# 				if k == 'id1':
	# 					a_video[k] = ObjectId(v)
	# 				else:
	# 					a_video[k] = v
	# user_m.save()


	#Get all courses of a user	
	# user_m = User_M.objects(id=4).first()
	# print(json.loads(user_m.to_json())['courses'])



	#Add or update a course. Send object id from client for existing course and object id blank for new course
		# post_data = {		
		# 	'domain': 'Web Development',
		# 	'certificate': 'Certified Associate in Web Development - Microservices',
		# 	'course_title': 'Microservices',
		# 	'owner': True,
		# 	'videos':[]		
		# 	# 'id1': bson.objectid.ObjectId("5d18800f9c983f0001ab3926")				
		# 	}
		
		# user_m = User_M.objects(id=5).get()

		# if 'id1' not in post_data.keys():		
		# 	a_course = Course_M()
		# 	for k, v in post_data.items():
		# 		a_course[k] = v
		# 	user_m.courses.create(**json.loads(a_course.to_json()))
		# else:
		# 	if not post_data['id1']:
		# 		a_course = Course_M()
		# 		for k, v in post_data.items():
		# 			a_course[k] = v
		# 		user_m.courses.create(**json.loads(a_course.to_json()))			
		# 	else:
		# 		a_course = user_m.courses.filter(id1=post_data['id1']).first()
		# 		for k, v in post_data.items():
		# 			a_course[k] = v
		# 		user_m.courses.update(**json.loads(a_course.to_json()))

		# user_m.save()
	

#Creating new user
	# new_userM = User_M(id=6,
	# 					firstname="Mary",
	# 					lastname="Flint",
	# 					email="rosh7@ikompass.com",
	# 					password="123"
	# 					)
			
			
	# new_userM.save()



#Accessing a user
	# user_m = User_M.objects(id=1).first()
	# print(user_m, file=sys.stderr)
	# print(type(user_m), file=sys.stderr)
	# user_dict = json.loads(user_m.to_json())
	# print(user_dict, file=sys.stderr)

#Creating or updating an new application which is a embedded document
	# post_data = {
	# 	'domain': 'Data Science',
	# 	'certificate': 'Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms',
	# 	'contact_lastname': 'Tina',
	# 	'contact_firstname': 'Prislan'
	# }

	
	# user_m = User_M.objects(id=1).first()
	# a_application = Application_M()
	# for k, v in post_data.items():
	# 	a_application[k] = v

	# print(json.loads(a_application.to_json()), file=sys.stderr)
	# user_m.add_or_replace_application(a_application)
	# user_m.save()

	#Accessing an application
			# application = User_M.objects(id=1).first().applications.filter(certificate="Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms").first()
	# certificate = "Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms"
	# application2 = User_M.objects.get(id=1).applications.filter(certificate=certificate).first()
	# print(json.loads(application2.to_json()))

	#Accessing an application if it does not exist
	# certificate = "Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms"
	# user_m = User_M.objects(id=1).first()
	# if user_m.applications.filter(certificate=certificate):
	# 	application = user_m.applications.get(certificate=certificate)
	# 	print(json.loads(application.to_json()))
	# print('No applications found for user')


	#Deleting an application
	# certificate = "Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms"
	# user_m = User_M.objects(id=1).first()
	# if user_m.applications.filter(certificate=certificate):
	# 	user_m.update(pull__applications__certificate=certificate)
	# 	print('deleted')
	# print('application not found')

	#Deleteing all applications
		# User_M.objects(id=1).first().update(set__applications=[])


@cli.command()
def test():
		tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
		result = unittest.TextTestRunner(verbosity=2).run(tests)
		if result.wasSuccessful():
			return 0
		return 1

@cli.command()
def seeddb():

	user1 = User(firstname='Tina', lastname='Prislan', email='tina.prislan@gmail.com', password='rakesh22')
	db.session.add(user1)
	# db.session.commit()

	# user = User.query.filter_by(email=user1.email).first()


	# application1 = Application(user_id=user.id,
	# 							domain='bigdata',
	# 							certificate='Certified Associate in Big Data (CABD) - Distributed Databases',
	# 							contact_firstname='Tina',
	# 							contact_lastname='Prislan',
	# 							contact_email='tina.prislan@gmail.com',
	# 							contact_streetaddress='41 Thomson Road',
	# 							contact_homecountry='Singapore',
	# 							contact_phonenumber='90900576',
	# 							contact_company_name='IKOMPASS'
	# 							)

	
	# db.session.add(application1)

	db.session.add(User(firstname='Ashwini', lastname='Rao', email='ashwini.rao@ikompass.com', password='rakesh22'))
	db.session.add(User(firstname='Deepak', lastname='G.S', email='aditya@ikompass.com', password='rakesh22'))

	


	db.session.commit()

# @cli.command()
def getcerts():
	certs_list = [{'Code': 1,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Programming Language'},
				 {'Code': 2,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Data Cleaning'},
				 {'Code': 3,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Data Analysis'},
				 {'Code': 4,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Data Visualization'},
				 {'Code': 5,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Data Acquisition'},
				 {'Code': 6,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Machine Learning Basics'},
				 {'Code': 7,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Linear Supervised Learning Algorithms'},
				 {'Code': 8,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Non-Linear Supervised Learning Algorithms'},
				 {'Code': 9,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Unsupervised Learning Algorithms'},
				 {'Code': 10,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Clustering Algorithms'},
				 {'Code': 11,
				  'domain': 'Data science',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
				  'title': 'Certified Associate in Data Science (CADS) - Deep Learning'},
				 {'Code': 12,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Programming Language'},
				 {'Code': 13,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Data Cleaning'},
				 {'Code': 14,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS)',
				  'title': 'Certified Professional in Data Science (CPDS)- Data Analysis'},
				 {'Code': 15,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Data Visualization'},
				 {'Code': 16,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Data Acquisition'},
				 {'Code': 17,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Machine Learning Basics'},
				 {'Code': 18,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Linear Supervised Learning Algorithms'},
				 {'Code': 19,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms'},
				 {'Code': 20,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Unsupervised Learning Algorithms'},
				 {'Code': 21,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Clustering Algorithms'},
				 {'Code': 22,
				  'domain': 'Data science',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
				  'title': 'Certified Professional in Data Science (CPDS) - Deep Learning'},
				 {'Code': 23,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Data Science Project Lifecycle'},
				 {'Code': 24,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Cleaning'},
				 {'Code': 25,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Analysis'},
				 {'Code': 26,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Reading visual charts'},
				 {'Code': 27,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Acquisition'},
				 {'Code': 28,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Machine Learning Basics'},
				 {'Code': 29,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Linear versus non-linear data'},
				 {'Code': 30,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Privacy issues'},
				 {'Code': 31,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Ethical issues'},
				 {'Code': 32,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Structured versus unstructured data'},
				 {'Code': 33,
				  'domain': 'Data science',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
				  'title': 'Certified Leader in Data Science (CLDS) - Data lake'},
				 {'Code': 34,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Programming Language'},
				 {'Code': 35,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Document Object Model'},
				 {'Code': 36,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Styling'},
				 {'Code': 37,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Request-Response cycle'},
				 {'Code': 38,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Application Structure (Example MVC)'},
				 {'Code': 39,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Templates'},
				 {'Code': 40,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Forms'},
				 {'Code': 41,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Databases'},
				 {'Code': 42,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Application Programming Interfaces'},
				 {'Code': 43,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Microservices'},
				 {'Code': 44,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - RESTful Web Services'},
				 {'Code': 45,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Programming Language'},
				 {'Code': 46,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Containers'},
				 {'Code': 47,
				  'domain': 'Web Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
				  'title': 'Certified Associate in Web Development (CAWD) - Front-end frameworks'},
				 {'Code': 48,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Programming Language'},
				 {'Code': 49,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Document Object Model'},
				 {'Code': 50,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Styling'},
				 {'Code': 51,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Request-Response cycle'},
				 {'Code': 52,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Application Structure (Example MVC)'},
				 {'Code': 53,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Templates'},
				 {'Code': 54,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Forms'},
				 {'Code': 55,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Databases'},
				 {'Code': 56,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Application Programming Interfaces'},
				 {'Code': 57,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Microservices'},
				 {'Code': 58,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - RESTful Web Services'},
				 {'Code': 59,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Programming Language'},
				 {'Code': 60,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Containers'},
				 {'Code': 61,
				  'domain': 'Web Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
				  'title': 'Certified Professional in Web Development (CPWD) - Front-end frameworks'},
				 {'Code': 62,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Front-end frameworks'},
				 {'Code': 63,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Web Application Project Lifecycle'},
				 {'Code': 64,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Architectures (Example Microservices)'},
				 {'Code': 65,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - SQL verus NoSQL databases'},
				 {'Code': 66,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Web Development Frameworks'},
				 {'Code': 67,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Application Programming Interfaces'},
				 {'Code': 68,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - RESTful Web Services'},
				 {'Code': 69,
				  'domain': 'Web Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
				  'title': 'Certified Leader in Web Development (CLWD) - Containerising'},
				 {'Code': 70,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Programming Language'},
				 {'Code': 71,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Native Applications for Android Platform'},
				 {'Code': 72,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Native Applications for iOS Platform'},
				 {'Code': 73,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Request-Response cycle'},
				 {'Code': 74,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Hybrid applications'},
				 {'Code': 75,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Forms'},
				 {'Code': 76,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Databases'},
				 {'Code': 77,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - Application Programming Interfaces'},
				 {'Code': 78,
				  'domain': 'Mobile Development',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
				  'title': 'Certified Associate in Mobile Development (CAMD) - RESTful Web Services'},
				 {'Code': 79,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Programming Language'},
				 {'Code': 80,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Native Applications for Android Platform'},
				 {'Code': 81,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Native Applications for iOS Platform'},
				 {'Code': 82,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Request-Response cycle'},
				 {'Code': 83,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Hybrid applications'},
				 {'Code': 84,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Forms'},
				 {'Code': 85,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - Databases'},
				 {'Code': 86,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD)',
				  'title': 'Certified Professional in Mobile Development (CPMD)- Application Programming Interfaces'},
				 {'Code': 87,
				  'domain': 'Mobile Development',
				  'framework': 'Professional',
				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
				  'title': 'Certified Professional in Mobile Development (CPMD) - RESTful Web Services'},
				 {'Code': 88,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Native Applications for Android Platform'},
				 {'Code': 89,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview Native Applications for iOS Platform'},
				 {'Code': 90,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Request-Response cycle'},
				 {'Code': 91,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Hybrid applications'},
				 {'Code': 92,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Progressive Web Applications'},
				 {'Code': 93,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Databases'},
				 {'Code': 94,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Application Programming Interfaces'},
				 {'Code': 95,
				  'domain': 'Mobile Development',
				  'framework': 'Leader',
				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
				  'title': 'Certified Leader in Mobile Development (CLMD) - Classifiers and regressors'},
				 {'Code': 95,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Ensemble Learning'},
				 {'Code': 96,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Detecting Patterns with Unsupervised Learning'},
				 {'Code': 97,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Building Recommender Systems'},
				 {'Code': 98,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Logic Programming'},
				 {'Code': 99,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Heuristic Search Techniques'},
				 {'Code': 100,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Natural Language Processing'},
				 {'Code': 101,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Building A Speech Recognizer'},
				 {'Code': 102,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Object Detection and Tracking'},
				 {'Code': 103,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Artificial Neural Networks'},
				 {'Code': 104,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Sensing devices'},
				  {'Code': 139,
				  'domain': 'Artificial Intelligence',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Computer Vision'},
				 {'Code': 105,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Inputs and End Points'},
				 {'Code': 106,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Communication and Information Theory'},
				 {'Code': 107,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Internet protocol and transmission control protocol'},
				 {'Code': 108,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Long-Range Communication Systems and Protocols (WAN)'},
				 {'Code': 109,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Routers and Gateways'},
				 {'Code': 110,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Cloud Protocols and Architectures'},
				 {'Code': 111,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Fog Topologies'},
				 {'Code': 112,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - IoT Security'},
				 {'Code': 113,
				  'domain': 'Internet of Things',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
				  'title': 'Certified Associate in Internet of Things (CAIoT) - Hardware virtualization'},
				 {'Code': 114,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Distributed Systems'},
				 {'Code': 115,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - CAP Theorm'},
				 {'Code': 116,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Decentralization'},
				 {'Code': 117,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Cryptography and Technical Foundations'},
				 {'Code': 118,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Mining'},
				 {'Code': 119,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Hash Functions'},
				 {'Code': 120,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Smart Contracts'},
				 {'Code': 121,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Hyperledger'},
				 {'Code': 122,
				  'domain': 'Blockchain',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
				  'title': 'Certified Associate in Blockchain (CABC) - Application-specific blockchains (ASBCs)'},
				 {'Code': 123,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed Storage'},
				 {'Code': 124,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed Processing'},
				 {'Code': 125,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - NoSQL'},
				 {'Code': 126,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Message brokers'},
				 {'Code': 127,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed File Systems'},
				 {'Code': 128,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Data Lake'},
				 {'Code': 129,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Lambda Architecture'},
				 {'Code': 130,
				  'domain': 'Big Data Technologies',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Privacy'},
				 {'Code': 131,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Data Encryption'},
				 {'Code': 132,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Public Key Infrastructure'},
				 {'Code': 133,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Physical Security Essentials'},
				 {'Code': 134,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Disaster Recovery'},
				 {'Code': 135,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Biometrics'},
				 {'Code': 136,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - System Security'},
				 {'Code': 137,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Access Controls'},
				 {'Code': 138,
				  'domain': 'Cyber Security',
				  'framework': 'Associate',
				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
				  'title': 'Certified Associate in Cyber Security (CACS) - Attacks and Countermeasures'}]

	return certs_list


# @cli.command()
# def seedcerts():
# 	certs_list = [{'Code': 1,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Programming Language'},
# 				 {'Code': 2,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Data Cleaning'},
# 				 {'Code': 3,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Data Analysis'},
# 				 {'Code': 4,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Data Visualization'},
# 				 {'Code': 5,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Data Acquisition'},
# 				 {'Code': 6,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Machine Learning Basics'},
# 				 {'Code': 7,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Linear Supervised Learning Algorithms'},
# 				 {'Code': 8,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Non-Linear Supervised Learning Algorithms'},
# 				 {'Code': 9,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Unsupervised Learning Algorithms'},
# 				 {'Code': 10,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Clustering Algorithms'},
# 				 {'Code': 11,
# 				  'domain': 'Data science',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Data Science (CADS) ',
# 				  'title': 'Certified Associate in Data Science (CADS) - Deep Learning'},
# 				 {'Code': 12,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Programming Language'},
# 				 {'Code': 13,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Data Cleaning'},
# 				 {'Code': 14,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS)',
# 				  'title': 'Certified Professional in Data Science (CPDS)- Data Analysis'},
# 				 {'Code': 15,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Data Visualization'},
# 				 {'Code': 16,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Data Acquisition'},
# 				 {'Code': 17,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Machine Learning Basics'},
# 				 {'Code': 18,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Linear Supervised Learning Algorithms'},
# 				 {'Code': 19,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Non-Linear Supervised Learning Algorithms'},
# 				 {'Code': 20,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Unsupervised Learning Algorithms'},
# 				 {'Code': 21,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Clustering Algorithms'},
# 				 {'Code': 22,
# 				  'domain': 'Data science',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Data Science (CPDS) ',
# 				  'title': 'Certified Professional in Data Science (CPDS) - Deep Learning'},
# 				 {'Code': 23,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Data Science Project Lifecycle'},
# 				 {'Code': 24,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Cleaning'},
# 				 {'Code': 25,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Analysis'},
# 				 {'Code': 26,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Reading visual charts'},
# 				 {'Code': 27,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Challenges in Data Acquisition'},
# 				 {'Code': 28,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Machine Learning Basics'},
# 				 {'Code': 29,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Linear versus non-linear data'},
# 				 {'Code': 30,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Privacy issues'},
# 				 {'Code': 31,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Ethical issues'},
# 				 {'Code': 32,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Structured versus unstructured data'},
# 				 {'Code': 33,
# 				  'domain': 'Data science',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Data Science (CLDS) ',
# 				  'title': 'Certified Leader in Data Science (CLDS) - Data lake'},
# 				 {'Code': 34,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Programming Language'},
# 				 {'Code': 35,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Document Object Model'},
# 				 {'Code': 36,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Styling'},
# 				 {'Code': 37,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Request-Response cycle'},
# 				 {'Code': 38,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Application Structure (Example MVC)'},
# 				 {'Code': 39,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Templates'},
# 				 {'Code': 40,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Forms'},
# 				 {'Code': 41,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Databases'},
# 				 {'Code': 42,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Application Programming Interfaces'},
# 				 {'Code': 43,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Microservices'},
# 				 {'Code': 44,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - RESTful Web Services'},
# 				 {'Code': 45,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Programming Language'},
# 				 {'Code': 46,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Containers'},
# 				 {'Code': 47,
# 				  'domain': 'Web Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Web Development (CAWD) ',
# 				  'title': 'Certified Associate in Web Development (CAWD) - Front-end frameworks'},
# 				 {'Code': 48,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Programming Language'},
# 				 {'Code': 49,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Document Object Model'},
# 				 {'Code': 50,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Styling'},
# 				 {'Code': 51,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Request-Response cycle'},
# 				 {'Code': 52,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Application Structure (Example MVC)'},
# 				 {'Code': 53,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Templates'},
# 				 {'Code': 54,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Forms'},
# 				 {'Code': 55,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Databases'},
# 				 {'Code': 56,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Application Programming Interfaces'},
# 				 {'Code': 57,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Microservices'},
# 				 {'Code': 58,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - RESTful Web Services'},
# 				 {'Code': 59,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Programming Language'},
# 				 {'Code': 60,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Containers'},
# 				 {'Code': 61,
# 				  'domain': 'Web Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Web Development (CPWD) ',
# 				  'title': 'Certified Professional in Web Development (CPWD) - Front-end frameworks'},
# 				 {'Code': 62,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Front-end frameworks'},
# 				 {'Code': 63,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Web Application Project Lifecycle'},
# 				 {'Code': 64,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Architectures (Example Microservices)'},
# 				 {'Code': 65,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - SQL verus NoSQL databases'},
# 				 {'Code': 66,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Web Development Frameworks'},
# 				 {'Code': 67,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Application Programming Interfaces'},
# 				 {'Code': 68,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - RESTful Web Services'},
# 				 {'Code': 69,
# 				  'domain': 'Web Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Web Development (CLWD) ',
# 				  'title': 'Certified Leader in Web Development (CLWD) - Containerising'},
# 				 {'Code': 70,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Programming Language'},
# 				 {'Code': 71,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Native Applications for Android Platform'},
# 				 {'Code': 72,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Native Applications for iOS Platform'},
# 				 {'Code': 73,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Request-Response cycle'},
# 				 {'Code': 74,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Hybrid applications'},
# 				 {'Code': 75,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Forms'},
# 				 {'Code': 76,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Databases'},
# 				 {'Code': 77,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - Application Programming Interfaces'},
# 				 {'Code': 78,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Mobile Development (CAMD) ',
# 				  'title': 'Certified Associate in Mobile Development (CAMD) - RESTful Web Services'},
# 				 {'Code': 79,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Programming Language'},
# 				 {'Code': 80,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Native Applications for Android Platform'},
# 				 {'Code': 81,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Native Applications for iOS Platform'},
# 				 {'Code': 82,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Request-Response cycle'},
# 				 {'Code': 83,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Hybrid applications'},
# 				 {'Code': 84,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Forms'},
# 				 {'Code': 85,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - Databases'},
# 				 {'Code': 86,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD)',
# 				  'title': 'Certified Professional in Mobile Development (CPMD)- Application Programming Interfaces'},
# 				 {'Code': 87,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Professional',
# 				  'sub_domain': 'Certified Professional in Mobile Development (CPMD) ',
# 				  'title': 'Certified Professional in Mobile Development (CPMD) - RESTful Web Services'},
# 				 {'Code': 88,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Native Applications for Android Platform'},
# 				 {'Code': 89,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview Native Applications for iOS Platform'},
# 				 {'Code': 90,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Request-Response cycle'},
# 				 {'Code': 91,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Hybrid applications'},
# 				 {'Code': 92,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Overview of Progressive Web Applications'},
# 				 {'Code': 93,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Databases'},
# 				 {'Code': 94,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Application Programming Interfaces'},
# 				 {'Code': 95,
# 				  'domain': 'Mobile Development',
# 				  'framework': 'Leader',
# 				  'sub_domain': 'Certified Leader in Mobile Development (CLMD) ',
# 				  'title': 'Certified Leader in Mobile Development (CLMD) - Classifiers and regressors'},
# 				 {'Code': 95,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Ensemble Learning'},
# 				 {'Code': 96,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Detecting Patterns with Unsupervised Learning'},
# 				 {'Code': 97,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Building Recommender Systems'},
# 				 {'Code': 98,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Logic Programming'},
# 				 {'Code': 99,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Heuristic Search Techniques'},
# 				 {'Code': 100,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Natural Language Processing'},
# 				 {'Code': 101,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Building A Speech Recognizer'},
# 				 {'Code': 102,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Object Detection and Tracking'},
# 				 {'Code': 103,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Artificial Neural Networks'},
# 				 {'Code': 104,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Sensing devices'},
# 				  {'Code': 139,
# 				  'domain': 'Artificial Intelligence',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Artificial Intelligence (CAAI) ',
# 				  'title': 'Certified Associate in Artificial Intelligence (CAAI) - Computer Vision'},
# 				 {'Code': 105,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Inputs and End Points'},
# 				 {'Code': 106,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Communication and Information Theory'},
# 				 {'Code': 107,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Internet protocol and transmission control protocol'},
# 				 {'Code': 108,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Long-Range Communication Systems and Protocols (WAN)'},
# 				 {'Code': 109,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Routers and Gateways'},
# 				 {'Code': 110,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Cloud Protocols and Architectures'},
# 				 {'Code': 111,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Fog Topologies'},
# 				 {'Code': 112,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - IoT Security'},
# 				 {'Code': 113,
# 				  'domain': 'Internet of Things',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Internet of Things (CAIoT) ',
# 				  'title': 'Certified Associate in Internet of Things (CAIoT) - Hardware virtualization'},
# 				 {'Code': 114,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Distributed Systems'},
# 				 {'Code': 115,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - CAP Theorm'},
# 				 {'Code': 116,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Decentralization'},
# 				 {'Code': 117,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Cryptography and Technical Foundations'},
# 				 {'Code': 118,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Mining'},
# 				 {'Code': 119,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Hash Functions'},
# 				 {'Code': 120,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Smart Contracts'},
# 				 {'Code': 121,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Hyperledger'},
# 				 {'Code': 122,
# 				  'domain': 'Blockchain',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Blockchain (CABC) ',
# 				  'title': 'Certified Associate in Blockchain (CABC) - Application-specific blockchains (ASBCs)'},
# 				 {'Code': 123,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed Storage'},
# 				 {'Code': 124,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed Processing'},
# 				 {'Code': 125,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - NoSQL'},
# 				 {'Code': 126,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Message brokers'},
# 				 {'Code': 127,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Distributed File Systems'},
# 				 {'Code': 128,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Data Lake'},
# 				 {'Code': 129,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Lambda Architecture'},
# 				 {'Code': 130,
# 				  'domain': 'Big Data Technologies',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Big Data Technologies (CABDT) ',
# 				  'title': 'Certified Associate in Big Data Technologies (CABDT) - Privacy'},
# 				 {'Code': 131,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Data Encryption'},
# 				 {'Code': 132,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Public Key Infrastructure'},
# 				 {'Code': 133,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Physical Security Essentials'},
# 				 {'Code': 134,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Disaster Recovery'},
# 				 {'Code': 135,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Biometrics'},
# 				 {'Code': 136,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - System Security'},
# 				 {'Code': 137,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Access Controls'},
# 				 {'Code': 138,
# 				  'domain': 'Cyber Security',
# 				  'framework': 'Associate',
# 				  'sub_domain': 'Certified Associate in Cyber Security (CACS) ',
# 				  'title': 'Certified Associate in Cyber Security (CACS) - Attacks and Countermeasures'}]
		 
# 	for each in certs_list:
# 		# db.session.add(Certificate(title=each['title'], domain=each['domain'], sub_domain=each['sub_domain'], framework=each['framework']))	
# 		# db.session.commit()

# 		new_cert = Certificate_M(
# 									title=each['title'],
# 									code=each['Code'],
# 									domain=each['domain'],
# 									framework=each['framework'],
# 									sub_domain=each['sub_domain']
# 								)
# 		new_cert.save()



@cli.command()
def addadmin():
	user = User(firstname='Roshan', lastname='Prakash', email='rosh@ikompass.com', password='rakesh22')
	user.admin = True
	db.session.add(user)	
	db.session.commit()



if __name__ == '__main__':
	cli()