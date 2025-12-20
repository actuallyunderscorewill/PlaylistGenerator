from GeneratePlaylist import playlist
filepath = '../../../Music/Music/Dollar Signs'
exclude = ['city without limits',
           'kavalier calm','avicii']
relative=True
x = playlist(filepath, exclude, relative=relative)
#x = playlist(exclude=exclude)
x.findmusic()
print(len(x.music))
#x.print()
x.save()
