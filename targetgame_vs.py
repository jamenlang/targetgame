#!/usr/bin/python
import RPi.GPIO as GPIO
import os
import time
import random
import pygame

os.chdir("/home/pi/targetgame")
GPIO.setmode(GPIO.BCM)

pygame.mixer.init()

#switches
target_switch = 18
weapon_switch = 23

#motor control
weapon_up = 17
weapon_down = 21
weapon_state_callback = 27
weapon_state = 0

#leds
led = 24

#hp
player_hp = 15
target_hp = 15

#gpio setup
GPIO.setup( led, GPIO.OUT )
GPIO.setup( target_switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )
GPIO.setup( weapon_switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )
GPIO.setup( weapon_up, GPIO.OUT )
GPIO.setup( weapon_down, GPIO.OUT )
GPIO.setup( weapon_state_callback, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )

#define variables
prev_input = 0
absorb = False
attack = False

#game is starting.
pygame.mixer.music.load( "intro.wav" )
pygame.mixer.music.play()

def blink( pin ):
 GPIO.output( pin, GPIO.HIGH )
 time.sleep( .5 )
 GPIO.output( pin, GPIO.LOW )
 time.sleep( .5 )
 return
for i in range( 0 , 56 ):
 blink( led )
 os.system( "clear" )
 print( "Get your weapons ready." )
 print( "Game Starting in: %d seconds." % ( 56 - i ) )

pygame.mixer.music.load( "loop.wav" )
pygame.mixer.music.play( -1 )

def raise_weapon( weapon_state ):
 while ( weapon_state != 1 ):
  print ( "waiting for weapon" )
  weapon_state = GPIO.input( weapon_state_callback )
  GPIO.output ( weapon_up, 1 )
 return ( weapon_state )

def lower_weapon( weapon_state ):
 while ( weapon_state != 0 ):
  #I'll have to count here because there is no callback for the 'lowered' state.
  print ( "waiting for weapon" )
  for i in range( 0, 5 ):
   GPIO.ouput ( weapon_down, 1 )
  weapon_state = GPIO.input( weapon_state_callback )
 return ( weapon_state )

def attackmode( player_hp, previous_input, iterations ):
 weapon_switch = 0
 weapon_state = GPIO.input( weapon_state_callback )
 os.system( "clear" )
 print( "Attack mode is ON" )
 iterations = iterations * 1000
 print( "Iterations %d" ) % iterations
 raise_weapon( weapon_state )

 while ( iterations != 0 ):
  input = GPIO.input( weapon_switch )
  if ( ( not prev_input ) and input ):
   os.system( "clear" )
   print ( "Player avoided damage!" )
   soundObj = pygame.mixer.Sound( "player_avoided_damage.wav" )
   soundObj.play()
   prev_input = input
   #slight pause to debounce
   time.sleep( 0.05 )
   lower_weapon( weapon_state )
   return ( target_hp, prev_input )
  iterations = iterations - 1

 player_hp = player_hp - 5
 os.system( "clear" )
 print ( "Player HP decreased to %d" ) % player_hp

 lower_weapon( weapon_state )

 soundObj = pygame.mixer.Sound( "player_damaged.wav" )
 soundObj.play()

 soundObj = pygame.mixer.Sound( "target_taunt.wav" )
 soundObj.play()

 return ( player_hp, prev_input )

def damagemode( target_hp , prev_input , iterations ):
 os.system( "clear" )
 print( "Damage mode is ON" )
 iterations = iterations * 100
 print( "Iterations %d" ) % iterations
 while ( iterations != 0 ):
  input = GPIO.input( target_switch )
  #print input
  if ( ( not prev_input ) and input ):
   print ( "Input: %d" ) % input
   print( "Target Damaged!" )
   target_hp = target_hp - 1
   print ( "Target HP Down to %d" ) % target_hp
   soundObj = pygame.mixer.Sound( "target_damaged.wav" )
   soundObj.play()

   prev_input = input
   return ( target_hp, prev_input )

   #slight pause to debounce
   time.sleep( 0.05 )
  iterations = iterations - 1
  #print iterations
 return ( target_hp, prev_input )

def absorbmode( target_hp, prev_input, iterations ):
 os.system( "clear" )
 print( "Absorb mode is ON" )
 iterations = iterations * 100
 print( "Iterations %d" ) % iterations
 GPIO.output( led, 1 )
 while ( iterations != 0 ):
  input = GPIO.input( target_switch )
  #print input
  if ( ( not prev_input ) and input ):
   print ( "Target absorbed damage!" )
   soundObj = pygame.mixer.Sound( "target_taunt.wav" )
   soundObj.play()

   target_hp = target_hp + 1
   print ( "Target HP increased to %d" ) % target_hp
   prev_input = input
   GPIO.output( led, 0 )
   return ( target_hp, prev_input )

   #slight pause to debounce
   time.sleep( 0.05 )
  iterations = iterations - 1

 GPIO.output( led, 0 )
 return ( target_hp, prev_input )

while True:
 prev_input = 0
 input = GPIO.input( target_switch )
 if ( ( not prev_input ) and input ):
  print ( "input %s, previously %s" ) % ( input, prev_input )
  print ( "Target HP: %d" ) % target_hp
 iterations = random.randrange( 1000, 10000 )

 if ( bool ( random.getrandbits ( 1 ) ) and absorb != False ):
  target_hp, prev_input = absorbmode( target_hp, prev_input, iterations )
  absorb = False
 else:
  absorb = bool( random.getrandbits ( 1 ) )

 if ( bool ( random.getrandbits ( 1 ) ) and attack != False ):
  player_hp, prev_input = attackmode( player_hp, prev_input, iterations )
  attack = False
 else:
  attack = bool( random.getrandbits ( 1 ) )

 target_hp, prev_input = damagemode( target_hp, prev_input, iterations )
 os.system( "clear" )
 print ( "Target HP: %d" ) % target_hp

 if ( target_hp <= 0 ):
  os.system( "clear" )
  print( "Target Destroyed!" )
  pygame.mixer.music.load ( "target_destroyed.wav" )
  pygame.mixer.music.play ()
  while pygame.mixer.music.get_busy() == True:
   continue
  break

 if ( player_hp <= 0 ):
  os.system( "clear" )
  print( "Player Destroyed!" )
  pygame.mixer.music.load ( "player_destroyed.wav" )
  pygame.mixer.music.play ()
  while pygame.mixer.music.get_busy() == True:
   continue
  break

 time.sleep( 1 )

GPIO.cleanup()
