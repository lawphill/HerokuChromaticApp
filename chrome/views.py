print "DEBUG: In views.py, before imports"

from flask import render_template, request, send_file
print "DEBUG: imported from flask"
from chrome import app
print "DEBUG: imported from chrome"
from chromatic import process_data, default_page
print "DEBUG: imported from chromatic"
#from pylab import plot, close, savefig, figure, title, xlabel, ylabel, grid
#from matplotlib import pyplot
print "DEBUG: Imported pyplot from matplotlib"
from pylab import plot, close, savefig, figure, title, xlabel, ylabel, grid
print "DEBUG: imported from pylab"
from StringIO import StringIO
print "DEBUG: imported from StringIO"

print "DEBUG: In views.py, made it past imports"

@app.route('/',methods=['POST','GET'])
@app.route('/index',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        c = process_data(request)
    else:
        c = default_page(request)

    print "Received a call to index page"

    return render_template("chromatic.html",
        c = c)

@app.route('/graphs/<n_prob>')
def cdf_plot(n_prob):
    # n_prob is a string, n = n_to_try, prob = prob_per_chrome
    n_to_try, prob_per_chrome = n_prob.split('_')
    n_to_try = int(n_to_try)
    prob_per_chrome = float(prob_per_chrome)

    nchromes = [i+1 for i in range(n_to_try)]
    cdf = [1-(1-prob_per_chrome)**(n+1) for n in range(n_to_try)]

    figure()
    cumprob = plot(nchromes,cdf,'b-')
    title('Probability of success after N chromes')
    xlabel('Number of Chromatic Orbs')
    ylabel('Cumulative Probabilitiy')
    grid(True)

    img = StringIO()
    savefig(img)
    close()
    img.seek(0)
    return send_file(img,mimetype='image/png')

@app.route('/howitworks')
def howitworks():
    return render_template("howitworks.html")
