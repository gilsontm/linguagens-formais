import glob, os

class AssertException(Exception):
	pass

def assert_true(exp):
	if exp is not True:
		raise AssertException()

def assert_false(exp):
	if exp is not False:
		raise AssertException()

def assert_equal(a, b):
	if a != b:
		raise AssertException()

def main():
	os.chdir("./")
	for file in glob.glob("*.py"):
		if file != 'test.py' and file.startswith('test'):
			print("Running " + file + ":")
			os.system("python3 " + file)

if __name__ == "__main__":
    main()
