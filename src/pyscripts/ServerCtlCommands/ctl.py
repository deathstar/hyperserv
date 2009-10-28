import sbserver
from xsbs.events import triggerServerEvent
from xsbs.commands import registerCommandHandler
from xsbs.settings import PluginConfig
from UserPrivilege.userpriv import masterRequired, adminRequired
from xsbs.colors import red, yellow, blue, green, colordict
from xsbs.plugins import reload as pluginReload
from xsbs.ui import error, info, insufficientPermissions
from Motd.motd import motdstring
import string

config = PluginConfig('servercommands')
servermsg_template = config.getOption('Templates', 'servermsg', '${orange}${sender}${white}: ${message}')
del config
servermsg_template = string.Template(servermsg_template)

@masterRequired
def onPauseCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #pause'))
		return
	sbserver.setPaused(True)

@masterRequired
def onResumeCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #resume'))
		return
	sbserver.setPaused(False)

@adminRequired
def onReloadCmd(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #reload'))
	else:
		sbserver.playerMessage(cn, yellow('NOTICE: ') + blue('Reloading server plugins.  Fasten your seatbelts...'))
		pluginReload()

@masterRequired
def onGiveMaster(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage #givemaster <cn>'))
		return
	try:
		tcn = int(args)
	except TypeError:
		sbserver.playerMessage(cn, error('Usage #givemaster <cn>'))
		return
	sbserver.playerMessage(cn, info('You have given master to %s') % sbserver.playerName(tcn))
	sbserver.setMaster(tcn)

@adminRequired
def onMasterMask(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #mastermask <int>'))
		return
	args = args.split(' ')
	sbserver.setMasterMask(int(args[0]))
	sbserver.message(info('Master mask is now %s') % args[0])

@adminRequired
def onResize(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #resize <int>'))
	else:
		size = int(args)
		sbserver.setMaxClients(int(args))

@masterRequired
def onMinsLeft(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #minsleft <int>'))
	else:
		sbserver.setMinsRemaining(int(args))

@masterRequired
def specAll(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #specall'))
	else:
		for s in sbserver.players():
			sbserver.spectate(s)

@masterRequired
def unspecAll(cn, args):
	if args != '':
		sbserver.playerMessage(cn, error('Usage: #unspecall'))
	else:
		for s in sbserver.spectators():
			sbserver.unspectate(s)

@masterRequired
def serverMessage(cn, args):
	if args == '':
		sbserver.playerMessage(cn, error('Usage: #servermsg <message>'))
	else:
		msg = servermsg_template.substitute(colordict, sender=sbserver.playerName(cn), message=args)
		sbserver.message(msg)

registerCommandHandler('pause', onPauseCmd)
registerCommandHandler('resume', onResumeCmd)
registerCommandHandler('reload', onReloadCmd)
registerCommandHandler('givemaster', onGiveMaster)
registerCommandHandler('mastermask', onMasterMask)
registerCommandHandler('resize', onResize)
registerCommandHandler('minsleft', onMinsLeft)
registerCommandHandler('specall', specAll)
registerCommandHandler('unspecall', unspecAll)
registerCommandHandler('servermsg', serverMessage)

