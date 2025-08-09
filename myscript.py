import pywikibot
from pywikibot import pagegenerators
site = pywikibot.Site('wikipedia:en')
sysops = site.allusers(group="sysop")
allsysops =[]

for sysop in sysops:
    groups = sysop['groups']
    if 'bot' in groups:
        print(sysop['name'])
    else:
        allsysops = allsysops+[sysop['name']]

print(allsysops)

#cat = pywikibot.Category(site,'Category:Living people')
#gen = pagegenerators.CategorizedPageGenerator(cat)
#for page in gen:
#    #Do something with the page object, for example:
#    text = page.text
#    print(text)

#"https://en.wikipedia.org/w/api.php?action=query&format=json&list=allusers&formatversion=2&augroup=sysop"