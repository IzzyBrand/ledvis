import visualizer
import sys

page = '''
<!DOCTYPE html>
<html>
<head>
    <script src='/static/jquery.min.js'></script>
    <script src='/static/popper.min.js'></script>
    <script src='/static/bootstrap.min.js'></script>
    <script src='/static/main.js'></script>
    <link rel='stylesheet' href='/static/css/bootstrap.min.css'/>
</head>

<body>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <center>
    <div class="btn-group-vertical btn-block" role="group" aria-label="Choose your mode">
{}
    </div>
    </center>
</body>
</html>
'''

button = '\t\t<button type="button" class="btn btn-{} btn-lg" onclick="btnClick(this, {})">{}</button>\n'
button_list = ''

for i, vis in enumerate(visualizer.vis_list):
	color = 'dark' if i==0 else 'light'
	button_list += button.format(color, i, vis().name)

page = page.format(button_list)


file = 'web/templates/index.html'
write = False

if len(sys.argv) > 1:
    if sys.argv[1] == '-f':
        write = True
    else:
        print 'Regenerate the webpage and write the output to {}. Use -f to skip check.'.format(file)
        sys.exit(0)
else:
    print(page)
    response = raw_input('[y/n] Do you want to write this to {}\t'.format(file))
    write = (response.lower() == 'y')

if write:
    f = open(file, 'w')
    f.write(page)
    f.close()
    print 'Written to {}'.format(file)
else:
    print 'Not writing.'
