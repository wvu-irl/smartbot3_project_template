import pygame
from smartbot_irl import Command


def get_key_command(sensors=None) -> Command:
    """
    Create a :class:`smartbot_irl.Command` object based on keyboard/mouse input.

    """

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                raise KeyboardInterrupt

    pygame.event.pump()
    keys = pygame.key.get_pressed()
    cmd = Command()

    lin_speed = 2
    ang_speed = 12.8

    if keys[pygame.K_UP]:
        cmd.linear_vel = lin_speed
    elif keys[pygame.K_DOWN]:
        cmd.linear_vel = -lin_speed
    else:
        cmd.linear_vel = 0.0

    if keys[pygame.K_LEFT]:
        cmd.angular_vel = ang_speed
    elif keys[pygame.K_RIGHT]:
        cmd.angular_vel = -ang_speed
    else:
        cmd.angular_vel = 0.0

    if keys[pygame.K_PAGEUP]:
        print('closing!')
        cmd.gripper_closed = True
    elif keys[pygame.K_PAGEDOWN]:
        print('opening!')
        cmd.gripper_closed = False

    if keys[pygame.K_b]:
        print('stowing!')
        cmd.manipulator_presets = 'STOW'
    elif keys[pygame.K_n]:
        print('holding!')
        cmd.manipulator_presets = 'HOLD'
    elif keys[pygame.K_m]:
        print('down-ing!')
        cmd.manipulator_presets = 'DOWN'

    return cmd
