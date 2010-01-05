from xsbs.events import eventHandler
from UserPrivilege.userpriv import masterRequired
from xsbs.ui import error
import sbserver

#modes where clients can swtich team
switchteam_modes = [
	4,
	6,
	8,
	10,
	11,
	12,
    14]

# modes where clients can set team name
setteam_modes = [
	2,
	4]

@eventHandler('player_switch_team')
@eventHandler('player_set_team')
def onSwitchTeam(cn, team):
	mode =  sbserver.gameMode()
	if mode in setteam_modes:
		sbserver.setTeam(cn, team)
	elif mode in switchteam_modes:
		if team == 'good' or team == 'evil':
			sbserver.setTeam(cn, team)
		else:
			sbserver.playerMessage(cn, error('You cannot join specified team in current game mode.'))
	else:
		sbserver.playerMessage(cn, error('You can not set team in this game mode.'))

