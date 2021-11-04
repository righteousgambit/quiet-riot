def handler(event, context):
	message = f'Hello {event["first_name"]} {event["last_name"]}!'
	return {'message': message, 'event': event}
