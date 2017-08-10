from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

class Menu_item_Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith('/restaurant'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				session = DBSession()

				output = ""
				output += "<html><body>"
				output += "<a href=/restaurant/new><h2>make a new restaurant here</h2><ul>"

				restaurants = session.query(Restaurant).all()

				for restaurant in restaurants:
					output += "<li>" + restaurant.name + "<br><a href=/%s/edit>edit</a> <br> <a href=/%s/delete>delete</a></li>"%(restaurant.id,restaurant.id)

				output += "</ul></body></html>"

				self.wfile.write(output.encode())

			if self.path.endswith('/restaurant/new'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><h1>make a new restaurant here</h1>"
				output += """<form method='POST' action='/restaurant/new'>
				<input name='restaurant_name' type='text'>
				<button type='submit' >submit</button></form>"""
				output += "</html></body>"
				self.wfile.write(output.encode())

			if self.path.endswith('/edit'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurant_id = self.path.split('/')[1]
				# print(restaurant_id)
				output = ""
				output += "<html><body><h1>edit the restaurant name here</h1>"
				output += """<form method='POST' action='/%s/edit'>
				<input name='new_name' type='text'>
				<button type='submit' >submit</button></form>"""%restaurant_id
				output += "</html></body>"
				self.wfile.write(output.encode())

			if self.path.endswith('/delete'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurant_id = self.path.split('/')[1]
				output = ""
				output += "<html><body><h1>are you sure you want to delete it?</h1>"
				output +=  """<form method='POST' action='/%s/delete'>
				<button type='submit' value = delete>delete</button></form>"""%restaurant_id
				output += """<form method='POST' action='/back'>
				<button type='submit' value = back>back</button></form>"""
				output += "</html></body>"
				self.wfile.write(output.encode())

		except IOError:
			self.send_error(404, "File Not Found %s" %self.path)

	def do_POST(self):
		try:
			length = int(self.headers.get('Content-length', 0))
			data = self.rfile.read(length).decode()
			session = DBSession()
			
			if self.path.endswith('/new'):
				print('new here')
				restaurant_name = parse_qs(data)['restaurant_name'][0]
				
				newRestaurant = Restaurant(name = restaurant_name)
				session.add(newRestaurant)
				session.commit()
			
			
			if self.path.endswith('edit'):
				restaurant_id = self.path.split('/')[1]
				
				target_restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)).one()
				target_restaurant.name = parse_qs(data)['new_name'][0]
				session.add(target_restaurant)
				session.commit()

			if self.path.endswith('delete'):
				print("click : " + self.path)
				restaurant_id = self.path.split('/')[1]
				target_restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)).one()
				session.delete(target_restaurant)
				session.commit()

			
			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.send_header('Location', '/restaurant')
			self.end_headers()

		except:
			print('something is wrong')
def main():
	try:
		port = 8080
		server = HTTPServer(('', port), Menu_item_Handler)
		print("Web server running on port %s" % port)
		server.serve_forever()

	except KeyboardInterrupt:
		print("^C entered, stopping web server...")
		server.socket.close()


if __name__ == '__main__':
	main()
