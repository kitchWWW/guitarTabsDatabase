#In short: 
# - assumes that the database has been built from a linear read/traversal of songsToDo
# - seeks through songsToDo and keeps only the ones after the last entry in the db


db = open('g_files/database.txt','r')
entries = db.readlines()
lastCompleteURL = entries[len(entries)-1].split('\t')[0]

songsToDo = open('g_files/songsToDo.txt','r+')
items = songsToDo.readlines()
todoList = []
found = False
for line in items:
	if line.strip('\n') == lastCompleteURL:
		found = True
		continue
	if found:
		todoList.append(line)
if not found:
	todoList = items
print 'remaining songs:', len(todoList)
songsToDo.seek(0)
for line in todoList:
	songsToDo.write(line)
songsToDo.truncate()
songsToDo.close()