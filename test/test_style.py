from pbpic import pbpstyle

def defaultStyle():
  return pbpstyle.Style(euler='lousy')

class Bar:
  pass

class Foo:
  defaultStyle = pbpstyle.Style(euler='ok')

class Baz:
  @staticmethod
  def defaultStyle():
    return pbpstyle.Style(euler='middling')

def test_getstyle():

	assert pbpstyle.getstyle(Bar, 'euler') == 'lousy'
	assert pbpstyle.getstyle(Bar, 'lagrange') == None

	b = Bar()
	assert pbpstyle.getstyle(b, 'euler') == 'lousy'
	assert pbpstyle.getstyle(b, 'lagrange') == None

	assert pbpstyle.getstyle(Foo,'euler') == 'ok'
	assert pbpstyle.getstyle(Baz,'euler') == 'middling'

def test_setstyle():
	b=Bar()
	pbpstyle.setstyle(b,euler='good')
	assert pbpstyle.getstyle(b,'euler')=='good'

def test_pushstyle():
	assert pbpstyle.getstyle(Foo,'euler') == 'ok'

	pbpstyle.setstyle(Foo,euler='great')
	pbpstyle.stylesave()

	pbpstyle.setstyle(Foo,euler='greatest')
	assert pbpstyle.getstyle(Foo,'euler') == 'greatest'
	pbpstyle.stylerestore()

	assert pbpstyle.getstyle(Foo,'euler') == 'great'

