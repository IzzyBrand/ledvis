import visualizer

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

button = '\t<button type="button" class="btn btn-{} btn-lg" onclick="btnClick(this, {})">{}</button>\n'
button_list = ''

for i, vis in enumerate(visualizer.vis_list):
	color = 'dark' if i==0 else 'light'
	button_list += button.format(color, i, vis().name)

print(page.format(button_list))

