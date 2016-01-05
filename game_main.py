import cocos, pyglet
import cocos.collision_model as cm
import cocos.euclid as eu
import random as r
import math

WIDTH, HEIGHT = 800, 600

class Game_main():
	def __init__(self):
		cocos.director.director.init(width = WIDTH, height = HEIGHT, caption = "Asteroids")

		try:
			scores_file = open("Highscores.txt")
			score_lines = scores_file.readlines()
			scores_file.close()
		except:
			score_lines = []
		self.highscores = []
		for line in score_lines:
			name, score = line.strip().split(': ')
			self.insert_highscore(int(score), name)

		self.start = Start()
		self.start_scene = cocos.scene.Scene(self.start)

		#cocos.director.director.set_show_FPS(True)
	def insert_highscore(self, score, name):
		
		def rank():
			for line in self.highscores:
				if score >= line[1]:
					return self.highscores.index(line)
			return len(self.highscores)

		if score == None:
			score = 0
		self.highscores.insert(rank(), (name, score))

		f = open('Highscores.txt', 'w')
		to_write = ''
		for line in self.highscores:
			to_write += line[0] + ': '+ str(line[1]) + '\n' 
		f.write(to_write)
		f.close()

	def new_game(self):
		self.level = 1
		self.score = 0

		self.arena = Arena(self.level)
		self.arena_scene = cocos.scene.Scene(self.arena)

		self.set_scene(self.arena_scene)

	def next_level(self):
		self.level += 1

		self.arena = Arena(self.level)
		self.arena_scene = cocos.scene.Scene(self.arena)

		self.set_scene(self.arena_scene)

	def end_game(self, did_win):
		self.end = End(did_win)
		self.end_scene = cocos.scene.Scene(self.end)

		self.set_scene(self.end_scene)

	def set_scene(self, scene):
		cocos.director.director.replace(scene)



class Start(cocos.layer.Layer):
	is_event_handler = True
	def __init__(self):
		super(Start, self).__init__()

		self.entities = []

		self.title = cocos.text.Label("Asteroids!",
			font_name = "Times New Roman",
			font_size = 32,
			anchor_x = 'center',
			anchor_y = 'center')
		self.title.position = 400, 400
		self.add(self.title)

		self.title = cocos.text.Label("Created by Brandon Webster",
			font_name = "Times New Roman",
			font_size = 16,
			anchor_x = 'center',
			anchor_y = 'center')
		self.title.position = 400, 360
		self.add(self.title)

		start_button = Start_button(400, 300)
		self.add(start_button.sprite)
		self.entities.append(start_button)

		self.mouse_pos = Vector2(0, 0)
		self.collisions = Collision_manager(self.entities)

		self.schedule(self.update)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_pos.set(x, y)

	def on_mouse_press(self, x, y, buttons, modifiers):
		is_clicked, entity = self.collisions.check_mouse(x, y)
		if is_clicked and entity.name == 'Start_button':
			game.new_game()

	def update(self, delta):
		pass

class Start_button():
	def __init__(self, x, y):
		self.pos = Vector2(x, y)

		self.name = 'Start_button'

		self.sprite = cocos.sprite.Sprite('start.png')
		self.sprite.position = self.pos.vec

		self.cshape = self.sprite.get_rect()

class End(cocos.layer.Layer):
	is_event_handler = True
	def __init__(self, did_win):
		super(End, self).__init__()

		self.entities = []

		self.did_win = did_win
		if not did_win:
			game.insert_highscore(game.score, '')

		self.results = cocos.text.Label("",
			font_name = "Times New Roman",
			font_size = 32,
			anchor_x = 'center',
			anchor_y = 'center')
		self.results.position = 400, 400
		if did_win:
			self.results.element.text = 'You Win!'
		else:
			self.results.element.text = 'You Lose!'
		self.add(self.results)

		self.score = cocos.text.Label("Level: " + str(game.level) + " Score: " + str(game.score),
			font_name = "Times New Roman",
			font_size = 16,
			anchor_x = 'center',
			anchor_y = 'center')
		self.score.position = 400, 300
		self.add(self.score)

		if did_win:
			start_text = 'Next Level'
		else:
			start_text = 'Try Again'
		self.start_label = cocos.text.Label(start_text,
			font_name = "Times New Roman",
			font_size = 16,
			anchor_x = 'center',
			anchor_y = 'center')
		self.start_label.position = 200, 350
		self.add(self.start_label)

		start_button = Start_button(200, 300)
		self.add(start_button.sprite)
		self.entities.append(start_button)

		end_button = End_button(600, 300)
		self.add(end_button.sprite)
		self.entities.append(end_button)

		self.mouse_pos = Vector2(0, 0)
		self.collisions = Collision_manager(self.entities)

		self.schedule(self.update)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_pos.set(x, y)

	def on_mouse_press(self, x, y, buttons, modifiers):
		is_clicked, entity = self.collisions.check_mouse(x, y)
		if is_clicked and entity.name == 'Start_button':
			if self.did_win:
				game.next_level()
			else:
				game.new_game()

		if is_clicked and entity.name == 'End_button':
			if self.did_win:
				game.insert_highscore(game.score, '')
			quit()

	def update(self, delta):
		pass

class End_button():
	def __init__(self, x, y):
		self.pos = Vector2(x, y)

		self.name = 'End_button'

		self.sprite = cocos.sprite.Sprite('close.png')
		self.sprite.position = self.pos.vec

		self.cshape = self.sprite.get_rect()



class Arena(cocos.layer.Layer):
	is_event_handler = True
	def __init__(self, level):
		super(Arena, self).__init__()

		batch = cocos.batch.BatchNode()
		self.add(batch)
		self.batch = batch

		self.laser_player = pyglet.media.Player()
		self.laser_player.volume = .4
		self.laser_sound = pyglet.resource.media('laser_sound.wav')
		self.laser_player.play()

		asteroid_count = level * 5
		self.ast_label = cocos.text.Label("Asteroids Remaining: " + str(asteroid_count),
			font_name = "Times New Roman",
			font_size = 16,
			anchor_x = 'left',
			anchor_y = 'top')
		self.ast_label.position = 10, HEIGHT - 10
		self.add(self.ast_label)

		self.laser_charge = 100
		self.charge_label = cocos.text.Label("Laser Charge: " + str(self.laser_charge),
			font_name = "Times New Roman",
			font_size = 16,
			anchor_x = 'left',
			anchor_y = 'top')
		self.charge_label.position = WIDTH - 175, HEIGHT - 10
		self.add(self.charge_label)

		self.overheat_label = cocos.text.Label("Overheated!",
			font_name = "Times New Roman",
			font_size = 32,
			color = (255, 75, 75, 1),
			anchor_x = 'center',
			anchor_y = 'center')
		self.overheat_label.opacity = 150
		self.overheat_label.visible = False
		self.overheat_label.position = WIDTH / 2, HEIGHT - 20
		self.add(self.overheat_label)

		self.key_names = []
		self.keys_pressed = set()

		self.top_ast_speed = 75 + 25 * game.level // 3

		self.entities = []
		for i in range(asteroid_count):
			x_or_y = r.randint(0, 1)
			if x_or_y == 0:
				test = Asteroid((r.randint(0, WIDTH), r.randint(0, 2) * HEIGHT), r.randrange(2, 8, 2), self.top_ast_speed)
			if x_or_y == 1:
				test = Asteroid((r.randint(0, 2) * WIDTH, r.randint(0, HEIGHT)), r.randrange(2, 8, 2), self.top_ast_speed)
			self.entities.append(test)

		self.ship = Ship((400., 300.))
		self.entities.append(self.ship)

		for elem in self.entities:
			batch.add(elem.sprite)

		self.collisions = Collision_manager(self.entities)

		self.schedule(self.update)

	def update(self, delta):
		if self.laser_player.time > .3:
			self.laser_player.next()

		if self.laser_charge < 15:
			self.overheat_label.visible = True
		else:
			self.overheat_label.visible = False

		asteroid_count = 0
		for elem in self.entities:
			elem.update(delta)
			if elem.name == 'Asteroid':
				asteroid_count += 1
		self.collisions.update_collidables(self.entities)

		self.ast_label.element.text = 'Asteroids Remaining: ' + str((asteroid_count))
		self.charge_label.element.text = 'Laser Charge: ' + str(int(self.laser_charge))

		if asteroid_count == 0:
			game.end_game(True)

	def update_charge(self, charge):
		self.laser_charge = charge

	def destroy(self, entity):
		try:
			self.batch.remove(entity.sprite)
		except Exception as e:
			print("Could not remove destroyed sprite: ", e)
		self.entities.remove(entity)

	def create(self, entity):
		self.batch.add(entity.sprite)
		self.entities.append(entity)

# ------ Input
	def on_key_press (self, key, modifiers):
	    self.keys_pressed.add(key)
	    self.update_input()

	def on_key_release (self, key, modifiers):
	    self.keys_pressed.remove(key)
	    self.update_input()

	def update_input(self):
		self.key_names = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]

class Collision_manager():
	def __init__(self, entities):
		self.collidables = [elem for elem in entities]

	def update_collidables(self, entities):
		self.collidables.clear()
		self.collidables = [elem for elem in entities]

	def check_mouse(self, x, y):
		for elem in self.collidables:
			if elem.cshape.contains(x, y):
				return True, elem
		return False, None

	def check_collisions(self, entity):
		for elem in self.collidables:
			if elem == entity:
				continue
			elif elem.cshape.overlaps(entity.cshape):
				return True, elem
		return False, None

class Entity():
	def __init__(self, pos):
		self.pos = Vector2(pos[0], pos[1])
		self.vel = Vector2(0, 0)
		self.acc = Vector2(0, 0)

		self.rot = 0
	
	def create_sprite(self, file_name, size):
		self.sprite = cocos.sprite.Sprite(file_name)
		self.sprite.position = self.pos.vec
		self.sprite.scale = size
		self.sprite.rotation = self.rot

		self.radius = (self.sprite.height + self.sprite.width) / 4
		self.cshape = cm.CircleShape(eu.Vector2(self.pos.x, self.pos.y), self.radius)

	def is_out(self):
		pos = self.pos
		if pos.x < 0 - self.size:
			return True, 'x1'
		elif pos.x > WIDTH + self.size:
			return True, 'x2'
		if pos.y < 0 - self.size:
			return True, 'y1'
		elif pos.y > HEIGHT + self.size:
			return True, 'y2'
		return False, 'no plane'
	def update(self, delta):
		self.vel = self.vel + self.acc * delta
		self.pos = self.pos + self.vel * delta

		value, plane = self.is_out()
		if value:
			if plane == 'x1':
				self.pos.x = WIDTH
			elif plane == 'x2':
				self.pos.x = 0
			elif plane == 'y1':
				self.pos.y = HEIGHT
			elif plane == 'y2':
				self.pos.y = 0


		self.cshape = cm.CircleShape(eu.Vector2(self.pos.x, self.pos.y), self.radius)
		self.sprite.position = self.pos.vec
		self.sprite.rotation = math.degrees(self.rot)

class Asteroid(Entity):
	def __init__(self, pos, size, top_speed):
		super().__init__(pos)

		self.name = 'Asteroid'

		self.vel = Vector2(r.randint(10, top_speed)*r.randrange(-1, 2, 2), r.randint(10, top_speed)*r.randrange(-1, 2, 2))

		self.size = size
		self.create_sprite('asteroid.png', self.size / 3)

	def hit(self, entity):
		if entity.name == 'Laser':
			game.score += 1
			if self.size > 2:
				self.size -= 2
				self.sprite.scale = self.size / 3
				game.arena.create(Asteroid((self.pos.x, self.pos.y), self.size, game.arena.top_ast_speed))
			else:
				game.arena.destroy(self)

class Ship(Entity):
	def __init__(self, pos):
		super().__init__(pos)

		self.name = 'Ship'

		self.power = 80
		self.size = 1
		self.create_sprite('Ship.png', self.size)

		self.reload_count = 15
		self.charge = 100

	def update(self, delta):
		if 'W' in game.arena.key_names or 'UP' in game.arena.key_names:
			self.acc.set(self.power * math.cos(self.rot), -1 * self.power * math.sin(self.rot))
		elif 'S' in game.arena.key_names or 'DOWN' in game.arena.key_names:
			self.acc.set(self.power * -1 * math.cos(self.rot), self.power * math.sin(self.rot))
		else:
			self.acc.set()

		if self.reload_count == 0 and 'SPACE' in game.arena.key_names and self.charge >= 10:
			laser = Laser((self.pos.x, self.pos.y), self.vel, self.rot)
			game.arena.create(laser)
			self.charge -= 10
			self.reload_count = 15
		elif self.reload_count > 0:
			self.reload_count -= 1

		if self.charge < 100:
			self.charge += .40
			game.arena.update_charge(self.charge)

		if 'A' in game.arena.key_names or 'LEFT' in game.arena.key_names:
			self.rot -= .075
		if 'D' in game.arena.key_names or 'RIGHT' in game.arena.key_names:
			self.rot += .075

		super().update(delta)

		is_colliding, col_entity = game.arena.collisions.check_collisions(self)
		if is_colliding and col_entity.name == 'Asteroid':
			game.end_game(False)

class Laser(Entity):
	def __init__(self, pos, vel, rot):
		super().__init__(pos)

		if game.arena.laser_player.playing:
			game.arena.laser_player.next()
		else:			
			game.arena.laser_player.play()
		game.arena.laser_player.queue(pyglet.resource.media('laser_sound.wav'))

		self.speed = 600
		self.vel = vel + Vector2(self.speed*math.cos(rot), - self.speed*math.sin(rot))
		self.rot = rot

		self.name = 'Laser'

		self.timer = 60
		self.size = .5
		self.create_sprite("laser.png", self.size)
		self.sprite.rotation = math.degrees(rot)

	def update(self, delta):
		self.timer -= 1
		alive = True
		if self.timer <= 0:
			game.arena.destroy(self)
			alive = False

		if alive:
			super().update(delta)

			is_colliding, col_entity = game.arena.collisions.check_collisions(self)
			if is_colliding and col_entity.name == 'Asteroid':
				col_entity.hit(self)
				game.arena.destroy(self)



class Vector2():
	def __init__(self, x = 0, y = 0):
		self.vec = (x, y,)
		self.x = x
		self.y = y
	def __str__(self):
		return str(self.pos)
	def __sub__(self, value):
		return Vector2(self.x - value.x, self.y - value.y)
	def __add__(self, value):
		return Vector2(self.x + value.x, self.y + value.y)
	def __mul__(self, value):
		return Vector2(self.x * value, self.y * value)
	def __truediv__(self, value):
		return Vector2(self.x / value, self.y / value)

	def set(self, x = 0, y = 0):
		self.vec = (x,y)
		self.x = x
		self.y = y

if __name__ == '__main__':
	game = Game_main()

	cocos.director.director.run(game.start_scene)
