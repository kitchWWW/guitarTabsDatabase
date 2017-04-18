#runs listBands with the letters we need
import os

args = [#'a','b','c','d','e','f','g','h','i','j','k',
'l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

for arg in args:
	os.system('python g_listBands.py '+arg)

#os.system('python g_listSongs.py')
#os.system('python g_processSongs')