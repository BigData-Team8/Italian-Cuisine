import re

removed = 0
modified = 0

postRules = {
	'replace': {
			'all': {

				'startsWith': {
					'il ': '',
					':': '',
					'|': '',
					'a ': '',
					'di ': '',
					"d'": '',
					'piccole di ': '',
					"' ": '',
					' a tra ': ' ',
					'd’ ': '',
					'Gr ': '',
					'Gr di ': '',
					'alla ': '',
					'alle ': '',
					'allo ': '',
					'all\' ': '',
					'“ ': '',
					'un\'': '',
					'bianco di ': '',
					'bianco medio ': '',
					'bianco secco ': '',
					'bianco edi ': '',
					'dadi di ': '',
					'disco sottile ': '',
					'sottile ': '',
					'etti ': '',
					'fogli ': '',
					'foglio ': '',
					'formaggio tipo': 'formaggio',
					'litrodi ': '',
					'loncino ': '',
					'oppure ': '',
					'ovettidi ': 'ovetti di ',
					'piedino ': '',
					'polpa d\'': '',
					'polpa di': '',
					'posteriore di ': '',
					'profumo di ': '',
					'punta di ': '',
					'pugno di ': '',
					'punte d\' ': '',
					'puntina di ': '',
					'quadrato di ': '',
					'rami di ': '',
					'“ ': '',
					'stelo di ': '',
					'stelle pasta': 'pasta',
					'tracce di ': '',
				},

				'endsWith': {
					' :': '',
					' di': '',
					' da': '',
					' )': '',
					' ,': '',
					' ,': '',
					" '": '',
					' un': '',
					' a': '',
					' e': '',
					' i': '',
					' o': '',
					' u': '',
					' in': '',
					' nè': '',
					' *': '',
					' %': '',
					' se': '',
					' :': '',
					' ma': '',
					' per': '',
					' ]': '',
					' al': '',
					' del': '',
					' gelato': '',
					' pari allo stesso peso': '',
					' nella centrale ': '',
					'colle duga damian princic': 'colle duga di damian princic',
					' di vari': '',
					' bollita': '',
					' lessa': '',
					' dimensioni': '',
					' rapida': '',
					' neutra': '',
					' q.b.': '',
					' al netto del': '',
					' al netto degli': '',
					' di uguale': '',
					' varie tipologie': '',
					' di diversi': '',
					' s.': '',
					' della larghezza': ''
				},

				'everywhere': {
					'cannelini': 'cannellini',
					'extrai': 'extra',
					'fagiuolini': 'fagiolini',
					'fagiooli': 'fagioli',
					'00\'': '00',
					'affumicataa': 'affumicataa',
					'pandispagna': 'pan di spagna',
					'semlolato': 'semolato',
					'yoghurt': 'yogurt',
					'uovaa': 'uova',
					'capperipiccoli': 'capperi',

					'\"': '',
					' , ': ', ',
					' ( ': ' ',
					' ( ': ' ',
					' %': '%',
					'd’ ': 'd\'',
					"' ": "'",
					'’': '\'',
					' - ': '-',
					',  ': ', ',
					'  ': ' ',
					"sott' ": "sott'",
					"un' ": "un'",
					"all' ": "all'",
					"l' ": "l'",
					'Péer': '',
					'\"': '',
					'  ': ' '				
				},

				'exactMatch': {
					'alcool %': 'alcool',
					'all\'olio': 'olio',
					'all\' olio': 'olio',
					'chi o fichi secchi': 'fichi secchi',
					'cipolla ramata': 'cipolla',
					'cipolla olio': 'cipolla',
					'cosce e sovracosce do pollo': 'cosce di pollo',
					'cotto di fichi': 'fichi',
					'cumino macinato': 'cumino',
					'd\' acciuga sottosale pinoli uvetta sultanina farina': 'acciuga sottosale',
					'dimarmellata d\' arance amara': 'marmellata di arance amare',
					'dipecorino': 'pecorino',
					'diversi tipi di pepe': 'pepe',
					'farina 180 w': 'farina',
					'farina tipo 0″': 'farina tipo 0',
					'farina tipo 2o farina 00': 'farina tipo 2',
					'filetti limone': 'limone',
					'filetti olio': 'olio',
					'filetto o controfiletto di vitello': 'filetto di vitello',
					'formaggio o pecorino': 'formaggio pecorino',
					'frutta tra mele more': 'frutta',
					'funghi o funghi secchi': 'funghi',
					'lievito x dolci': 'lievito',
					'limone arancia': 'limone',
					'maltagliati uovo': 'maltagliati all\'uovo',
					'manzo taglio anteriore': 'manzo',
					'maraschino °': 'maraschino',
					'marmellata \' albicocche': 'marmellata d\' albicocche',
					'marmellata arance amare': 'marmellata d\'arance amare',
					'meringa centimetri ognuno': 'meringa',
					'merluzzo dal peso': 'merluzzo',
					'mezzemaniche n32 garofalo': 'mezze maniche',
					'molica di pane': 'mollica di pane',
					'mompariglia': 'mom pariglia',
					'moscardini seppioline - vongole': 'moscardini',
					'occhi d\' avena': 'fiocchi d\'avena',
					'olio dimandorle': 'olio di mandorle',
					'olio extravergine di oliva sale': 'olio extravergine di oliva sale',
					'ori di zucca': 'fiori di zucca',
					'paio timo': 'timo',
					'pane del tipo': 'pane',
					'pane piccanti': 'pane piccante',
					'pane tostate': 'pane tostato',
					'panino che abbia mollica': 'panino',
					'pannamontata': 'panna',
					'pari spinaci': 'spinaci',
					'parma sant\' ilario stagionato': 'prosciutto di parma',
					'parmigian': '',
					'parmigiano per il ripieno': 'parmigiano',
					'passion': 'passion fruit',
					'pastina del formato adatto all\' età': 'pastina',
					'pepi': 'pepe',
					'pesce misto cozze': 'pesce misto',
					'pesci di diverso tipo': 'pesci vari',
					'pesci diversi': 'pesci vari',
					'petto pollo': 'petto di pollo',
					'piada di farro olio d\' oliva': 'piadina di farro',
					'piselli piselli surgelati': 'piselli',
					'petto di pollo lesso': 'petto di pollo',
					'pollo lesso': 'pollo',
					'primosale': 'primo sale',
					'retato': 'popone retato',
					'salsiccette carne': 'salsiccette di carne',
					'seppia da 700/800': 'seppia',
					'sorbetto di vari': 'sorbetto',
					'spiacchio d\' ': '',
					'spiacchiod\'': '',
					'spicchi d\' ': '',
					'succodi': 'succo di',
					'sugo d\' d\' anatra': 'sugo d\'anatra',
					'susine di vario colore': 'susine',
					'tagli gamba di manzo': 'manzo',
					'top di panna liquida': 'panna',
					'topinambour': 'topinambur',
					'uovo di gallina allevata': 'uovo',
					'uova tuorlo': 'tuorlo di uovo',
					'uva tra bianca e nera': 'uva',
					'vanillina cannella': 'vanillina',
					'ventresca di tonno olio': 'ventresca di tonno',
					'vino bianco secco 3 uova': 'vino bianco',
					'zucchero al velo': 'zucchero a velo',
					'zucchero avelo': 'zucchero a velo',
					'zuccheroa velo': 'zucchero a velo',
					'zucchero semolato pari al peso dei datteri': 'zucchero semolato'
				}
			},

			'amount': {
				'equals': {
					'un': '1',
					'di': '',
					'e': '',
					'per': '',
					'|': '',
					'\"': '',
					'"': '',
					'1⁄2': '1/2'
				}
			}
	},

	'remove': {
		'ingredient': {
			'equals': [ 
				'impasto base per',
				'altri ingredienti :',
				'tipo digestive',
				'variazione livanto',
				'carta',
				'casalinga',
				'caserecce',
				'catalogna',
				'medio',
				'celeste',
				'estrusi',
				'cialde',
				'cialdine',
				'ciascuna',
				'cimette',
				'concentrato',
				'contorno :',
				'coscia',
				'cosciotto d',
				'cosciotto',
				'costine',
				'cotte',
				'cotto',
				'decorticato',
				'del ripieno preferito',
				'dessert',
				'di diverso colore',
				'di garofano',
				'di granatina',
				'di preparato',
				'di sapori % naturale da plasmon',
				'di sughero',
				'd\' osso',
				'enrico',
				'erbe composto di :',
				'duro pugliese',
				'fine',
				'finissimo',
				'fiori di',
				'fondant',
				'fondente',
				'fondente di zucchero color cioccolato',
				'forte',
				'già e',
				'giallo',
				'gola',
				'impasto',
				'liofilizzato',
				'lollo',
				'mazzetto',
				'meglio se del tipo dolce',
				'medaglioni d\'',
				'moscata',
				'musica',
				'nissimo',
				'nodini',
				'occhiata',
				'odoroso',
				'ogliarola',
				'olandese',
				'delicato',
				'ovoli maggiorana',
				'ovoli',
				'palla',
				'paninetti',
				'pasquale'
				'pelle',
				'per',
				'petto d\'',
				'piccante',
				'pipe',
				'poca',
				'poco',
				'polpa d\'',
				'possibilmente nero',
				'pozzoferrato storchi',
				'praga spessa pari',
				'raspatura',
				'ricetta',
				'ripieno',
				'roast',
				'rosso',
				'sacchetti da freezer'
				'salty fingers koppert cress',
				'sammarzano',
				'raffermo',
				'sampietro',
				'san daniele',
				'san pietro',
				'secco',
				'seconda mousse :',
				'sporche',
				'solubile',
				'spada',
				'spada di',
				'spago da cucina',
				'spagna',
				'spalmabile',
				'spalmare',
				'spezzatino',
				'spezzatino d\'',
				'spicchi',
				'spicchio',
				'spiedini lunghi',
				'spray mini di silikomart',
				'spray staccante',
				'stracci',
				'strisce buccia',
				'strizzati e tritatissimi',
				'sugo d\'',
				'testi',
				'trevisana',
				'vasetti'
				'velò',
				'vegetali',
				'zolletta',
				'zollette'
			],
			'startsWith': [ ' NULL ' ]
		}
	},

	# strip everything after one of the following keywords
	'endingTokens' : [ ' o ', ' e ', ' formato ', ' per ', ' come ', ' / ' ],

	'stopWords':  [
		' abbondante ',
		' abbondanti ', 
		' etichetta ',
		' mista ',
		' piacciono' 
		' dallo ',
		' andrea ',
		' anelli ',
		' spesso ',
		' spessa ',
		' affettato ',
		' scelta ',
		' sodo ',
		' maturo ',
		' barattolo ',
		' pronto ',
		' pronte ',
		' densa ',
		' denso ',
		' sbollentata ',
		' bocconcini ',
		' bottiglie ',
		' bottigline' 
		' caldo ',
		' necessario ',
		' buon ',
		' buoni ',
		' sciolto ',
		' morbidissimo ',
		' bustinadi ',
		' bustina ',
		' ben ',
		' fritti ',
		' fritto ',
		' avanzata ',
		' medio ',
		' estrusi' 
		' cestino ',
		' cestini ',
		' ghiacciatissimo ',
		' ghiacciato ',
		' chilo ',
		' preferibilmente ',
		' circa ',
		' minimo ',
		' ciotole ',
		' ciotola ',
		' affettate ',
		' affettato ',
		' nuove ',
		' nuovo ',
		' ciuffi ',
		' ciuffetti ',
		' colmo ',
		' confezioni ',
		' coste ',
		' così ',
		' ottenuta ',
		' cubetti ',
		' cubetto ',
		' cucchaino ',
		' cucchiaidi ',
		' cucchiaiate ',
		' cucchiaiata ',
		' cucchiaini ',
		' dadolata ',
		' marca ',
		' disco ',
		' dischi ',
		' diametro ',
		' doppione ',
		' facoltativi ',
		' facoltativo ',
		' gocce' 
		' frigorifero' 
		' grandi ',
		' grande ',
		' grappoli ',
		' grappolino ',
		' stessa' 
		' grosse ',
		' grossi ',
		' vuoti ',
		' inoltre ',
		' proseguimento ',
		' pura ',
		' purissima ',
		' lunghi ',
		' intero ',
		' alleggerita ',
		' manciatina ',
		' frullato ',
		' freddo ',
		' latteria ',
		' mazzo' 
		' molto ',
		' vergine ',
		' mix ',
		' qualità ',
		' palla ',
		' palline ',
		' abbrustolite ',
		' abbrustolito ',
		' parti' 
		' sugose ',
		' pezzi ',
		' piccoli ',
		' piccole ',
		' piccolissimi ',
		' poco ',
		' pochissimo ',
		' pezzetti ',
		' appesi ',
		' sodi ',
		' appena ',
		' giovani ',
		' generosi ',
		' legato ',
		' avanzata ',
		' possibilmente ',
		' rondelle ',
		' commestibili ',
		' appena ',
		' germogliato ',
		' rotolo ',
		' grossines' 
		' sbollentate ',
		' scaglie ',
		' scatola ',
		' scatolina ',
		' scorza ',
		' scrozette ',
		' monoporzione ',
		' soqquadri ',
		' stecca ',
		' stecchi ',
		' strisce ',
		' striscia' 
		' surgelate ',
		' surgelati ',
		' trito ',
		' eviscerate ',
		' tubi ',
		' tutto ',
		' preferibilmente ',
		' vaschetta ',
		' vaschette ',
		' vasetti ',
		' finissimo ',
		' extrafino ',
		' extrafine ' 
	]

}

preRules = {
	'replace': {
		'everywhere': {
				"\\u2028": ' ',
				"\\\\u2028": ' ',
				"\\u2028": ' ',
				"\\\\u2028": ' ',				
				"\\xa0": ' ',
				"\\\\xa0": ' '
		}

	},
	'remove': {
		'everywhere': [ 'lista ' ]
	}
}

def replaceRight(source, target, replacement, replacements = None):
    return replacement.join(source.rsplit(target, replacements))

def postCleaner(ingredient, amount):

	global modified
	global removed

	ingredient = ingredient.strip()
	orig = ingredient
	amount = amount.strip()

	for match in postRules['remove']['ingredient']['equals']:
		if (ingredient == match):
			# print('removed ' + ingredient)
			ingredient = ''
			removed += 1
			return

	for match in postRules['remove']['ingredient']['startsWith']:
		if (ingredient.startswith(match)):
			# print('removed ' + ingredient)			
			ingredient = ''
			removed += 1
			return

	for match in postRules['replace']['all']['exactMatch']:
		rule = postRules['replace']['all']['exactMatch'][match]
		if (ingredient == match): ingredient = rule

	for match in postRules['replace']['all']['everywhere']:
		rule = postRules['replace']['all']['everywhere'][match]
		ingredient = ingredient.replace(match, rule)
		amount = amount.replace(match, rule)

	# remove all after an ending token
	for token in postRules['endingTokens']:
		result = ingredient.rsplit(token, 1)
		if (len(result) > 1): ingredient = result[0]
	
	"""
	for match in postRules['replace']['amount']['equals']:
		rule = postRules['replace']['amount']['equals'][match]
		if (amount == match): amount = rule
	"""

	for match in postRules['replace']['all']['startsWith']:
		rule = postRules['replace']['all']['startsWith'][match]
		if ingredient.startswith(match): ingredient = ingredient.replace(match, rule, 1)
		if amount.startswith(match): amount = amount.replace(match, rule, 1)

	for match in postRules['replace']['all']['endsWith']:
		rule = postRules['replace']['all']['endsWith'][match]
		if ingredient.endswith(match): ingredient = replaceRight(ingredient, match, rule, 1)
		if amount.endswith(match): amount = replaceRight(amount, match, rule, 1)

	# remove all stopwords
	for token in postRules['stopWords']:
		ingredient = ' ' + ingredient + ' '
		ingredient = ingredient.replace(token, ' ')

		ingredient = ingredient.strip()

	for match in postRules['replace']['all']['startsWith']:
		rule = postRules['replace']['all']['startsWith'][match]
		if ingredient.startswith(match): ingredient = ingredient.replace(match, rule, 1)
		if amount.startswith(match): amount = amount.replace(match, rule, 1)

	for match in postRules['replace']['all']['endsWith']:
		rule = postRules['replace']['all']['endsWith'][match]
		if ingredient.endswith(match): ingredient = replaceRight(ingredient, match, rule, 1)
		if amount.endswith(match): amount = replaceRight(amount, match, rule, 1)

	for match in postRules['replace']['all']['everywhere']:
		rule = postRules['replace']['all']['everywhere'][match]
		ingredient = ingredient.replace(match, rule)
		amount = amount.replace(match, rule)

	ingredient = ingredient.strip()
	amount = amount.strip()

	# print(orig + '\n' + ingredient + '\n')
	
	if (orig != ingredient): modified += 1

	# ingredient = ingredient.capitalize()

	return [ ingredient, amount ]

def preCleaner(ingredient):
	# remove the content inside parentheses
	ingredient = re.sub(r'\([^)]*\)', '', ingredient)

	for match in preRules['replace']['everywhere']:
		rule = preRules['replace']['everywhere'][match]
		ingredient = ingredient.replace(match, rule)

	for match in preRules['remove']['everywhere']:
		if match in ingredient: ingredient = ''

	return ingredient
