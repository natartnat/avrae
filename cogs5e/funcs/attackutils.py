from cogs5e.models import embeds
from utils.functions import a_or_an


async def run_attack(ctx, embed, args, caster, attack, targets, combat):
    """
    Runs an attack: adds title, handles -f and -thumb args, commits combat, runs automation, edits embed.

    :type ctx: discord.ext.commands.Context
    :type embed: discord.Embed
    :type args: utils.argparser.ParsedArguments
    :type caster: cogs5e.models.sheet.statblock.StatBlock
    :type attack: cogs5e.models.sheet.attack.Attack
    :type targets: list of str or list of cogs5e.models.sheet.statblock.StatBlock
    :type combat: None or cogs5e.models.initiative.Combat
    """
    if not args.last('h', type_=bool):
        name = caster.get_title_name()
    else:
        name = "An unknown creature"

    if not attack.proper:
        attack_name = a_or_an(attack.name)
    else:
        attack_name = attack.name

    verb = attack.verb or "attacks with"

    if args.last('title') is not None:
        embed.title = args.last('title') \
            .replace('[name]', name) \
            .replace('[aname]', attack_name)
    else:
        embed.title = f'{name} {verb} {attack_name}!'

    # arg overrides (#1163)
    arg_defaults = {
        'criton': attack.criton, 'phrase': attack.phrase, 'thumb': attack.thumb, 'c': attack.extra_crit_damage
    }
    args.update_nx(arg_defaults)

    await attack.automation.run(ctx, embed, caster, targets, args, combat=combat, title=embed.title)
    if combat:
        await combat.final()

    embeds.add_fields_from_args(embed, args.get('f'))
    if 'thumb' in args:
        embed.set_thumbnail(url=args.last('thumb'))
