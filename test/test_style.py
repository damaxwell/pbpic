from pbpic import style

# def defaultStyle():
#   return style.Style(euler='lousy')

class Foo:
  pass
  # defaultStyle = style.Style(euler='ok')
  # @staticmethod
  # def defaultStyle():
  #   return style.Style(euler='ok')

print style.style(Foo,'euler')
style.setstyle(Foo,euler='great')
style.stylesave()
style.setstyle(Foo,euler='greatest')
print style.style(Foo,'euler')
style.stylerestore()
print style.style(Foo,'euler')

