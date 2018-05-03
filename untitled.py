
def csv_fy(display):
	def wrapper(*args, **kwargs):
		print("Inside the wrapper")
		display(*args, **kwargs)
		print("After the display function")
        return wrapper
        
@csv_fy
def display(*args):
	print ([i + " " for i in args])
	

	
def main():
	display("Hello World!", "I have arrived")
	return 0

if __name__ == '__main__':
    main()

