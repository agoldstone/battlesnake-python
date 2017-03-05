import bottle
import os
import math

#let 0 represent nothing in that spot
#let 1 represent snakes
#let 2 represent food
#let 3 be a bad spot
#let 4 represent a safe space

def direction(from_cell, to_cell):
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]

    if dx == 1:
        return 'right'
    elif dx == -1:
        return 'left'
    elif dy == -1:
        return 'up'
    elif dy == 1:
        return 'down'

def init(data):
	board = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
	
	#food
	for f in data['food']:
		board[f[0]][f[1]] = 2
		
	for s in data['snakes']:
		if s['id'] == data['you']:
			oursnake = s
		for c in s['coords']:
			board[c[0]][c[1]] = 1
			
	return oursnake, board
	
def distance(p, q):
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
    return dx + dy;
	
@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
		'secondary_color': '#FF0000',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python',
		'head_type': type,
		'tail_type': type
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
	
	oursnake, board = init(data)
	
	#making move decision here
	#have a max distance to other snakes
	#check if a possible move will block self in
	#check if will be too close to another snake
	for bsnakes in data['snakes']:
		if(bsnakes['id'] == data['you']):
			#move to next snake
			continue
		#check distance from oursnake
		#mark good or bad moves off of this data
		if(distance(oursnake['coords'][0], bsnakes['coords'][0]) > 3):
			continue
		#if here then other snakes are close
		bsx = bsnakes['coords'][0][0]
		bsy = bsnakes['coords'][0][1]
		
		if(bsx < data['width']-1):
			#mark as safe space
			board[bsx + 1][bsy] = 4
		if(bsx > 0):
			board[bsx -1][bsy] = 4
		if(bsy < data['height']-1):
			board[bsx][bsy + 1] = 4
		if(bsy > 0):
			board[bsx][bsy -1] = 4
			
	#move to a 4 if possible or a 2
	#check the 3 spaces surrounding oursnake head
	#have above, below, toright, toleft
	ourheadx = oursnake['coords'][0][0]
	ourheady = oursnake['coords'][0][1]
	
	#check above
	#if outofbounds then move on
	if(ourheadx < data['width']-1):
		#not agaist edge
		#right of the head is good
		toright = board[ourheadx +1][ourheady]
	else:
		#toright is a no go
		toright = 3
		
	if(ourheadx > 0):
		#not agaist other edge
		#left of head is good
		toleft = board[ourheadx - 1][ourheady]
	else:
		#toleft is no good
		toleft = 3
		
	if(ourheady < data['height']-1):
		#below head is good
		below = board[ourheadx][ourheady +1]
	else:
		#below is no good
		below = 3
		
	if(ourheady > 0):
		#above head is good
		above = board[ourheadx][ourheady -1]
	else:
		#above is no good
		above = 3
		
	#go through the directions and choose a 4 or 2 or 0
	if(toright%2 == 0):
		destination = [ourheadx+1,ourheady]
		if((toleft%2 == 0)and(toleft > toright)):
			destination = [ourheadx-1,ourheady]
		elif((below %2 == 0)and(below > toright)):
			destination = [ourheadx,ourheady+1]
		elif((above%2 == 0)and(above > toright)):
			destination = [ourheadx,ourheady -1]
			
	if(toleft%2 == 0):
		destination = [ourheadx-1,ourheady]
		if((toright%2 == 0)and(toright > toleft)):
			destination = [ourheadx+1,ourheady]
		elif((below %2 == 0)and(below > toleft)):
			destination = [ourheadx,ourheady+1]
		elif((above%2 == 0)and(above > toleft)):
			destination = [ourheadx,ourheady -1]
			
	if(below%2 == 0):
		destination = [ourheadx,ourheady+1]
		if((toleft%2 == 0)and(toleft > below)):
			destination = [ourheadx-1,ourheady]
		elif((toright %2 == 0)and(toright > below)):
			destination = [ourheadx+1,ourheady]
		elif((above%2 == 0)and(above > below)):
			destination = [ourheadx,ourheady -1]
			
	if(above%2 == 0):
		destination = [ourheadx,ourheady-1]
		if((toleft%2 == 0)and(toleft > above)):
			destination = [ourheadx-1,ourheady]
		elif((below %2 == 0)and(below > above)):
			destination = [ourheadx,ourheady+1]
		elif((toright%2 == 0)and(toright > above)):
			destination = [ourheadx +1,ourheady]
	#move is the direction from oursnake head to open space(destination)
	#coords are like [1,1]
	m = direction(oursnake['coords'][0], destination)
    return {
        'move': m,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
