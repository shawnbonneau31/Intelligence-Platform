"""
Namara Water Risk Intelligence Platform — Risk Scoring Engine
Composite scoring across 7 data layers: Claims, Climate, Water Quality, Infrastructure, Pressure, Builder Quality, Regulatory.
"""

import requests
import sqlite3
import hashlib
import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "namara.db")

# ─── ZIP → State mapping (909 prefix entries) ───
ZIP_TO_STATE = {
    "005":"NY","006":"PR","007":"PR","008":"VI","009":"PR","010":"MA","011":"MA","012":"MA",
    "013":"MA","014":"MA","015":"MA","016":"MA","017":"MA","018":"MA","019":"MA","020":"MA",
    "021":"MA","022":"MA","023":"MA","024":"MA","025":"MA","026":"MA","027":"MA","028":"RI",
    "029":"RI","030":"NH","031":"NH","032":"NH","033":"NH","034":"NH","035":"NH","036":"NH",
    "037":"NH","038":"NH","039":"ME","040":"ME","041":"ME","042":"ME","043":"ME","044":"ME",
    "045":"ME","046":"ME","047":"ME","048":"ME","049":"ME","050":"VT","051":"VT","052":"VT",
    "053":"VT","054":"VT","055":"VT","056":"VT","057":"VT","058":"VT","059":"VT","060":"CT",
    "061":"CT","062":"CT","063":"CT","064":"CT","065":"CT","066":"CT","067":"CT","068":"CT",
    "069":"CT","070":"NJ","071":"NJ","072":"NJ","073":"NJ","074":"NJ","075":"NJ","076":"NJ",
    "077":"NJ","078":"NJ","079":"NJ","080":"NJ","081":"NJ","082":"NJ","083":"NJ","084":"NJ",
    "085":"NJ","086":"NJ","087":"NJ","088":"NJ","089":"NJ","100":"NY","101":"NY","102":"NY",
    "103":"NY","104":"NY","105":"NY","106":"NY","107":"NY","108":"NY","109":"NY","110":"NY",
    "111":"NY","112":"NY","113":"NY","114":"NY","115":"NY","116":"NY","117":"NY","118":"NY",
    "119":"NY","120":"NY","121":"NY","122":"NY","123":"NY","124":"NY","125":"NY","126":"NY",
    "127":"NY","128":"NY","129":"NY","130":"NY","131":"NY","132":"NY","133":"NY","134":"NY",
    "135":"NY","136":"NY","137":"NY","138":"NY","139":"NY","140":"NY","141":"NY","142":"NY",
    "143":"NY","144":"NY","145":"NY","146":"NY","147":"NY","148":"NY","149":"NY","150":"PA",
    "151":"PA","152":"PA","153":"PA","154":"PA","155":"PA","156":"PA","157":"PA","158":"PA",
    "159":"PA","160":"PA","161":"PA","162":"PA","163":"PA","164":"PA","165":"PA","166":"PA",
    "167":"PA","168":"PA","169":"PA","170":"PA","171":"PA","172":"PA","173":"PA","174":"PA",
    "175":"PA","176":"PA","177":"PA","178":"PA","179":"PA","180":"PA","181":"PA","182":"PA",
    "183":"PA","184":"PA","185":"PA","186":"PA","187":"PA","188":"PA","189":"PA","190":"PA",
    "191":"PA","192":"PA","193":"PA","194":"PA","195":"PA","196":"PA","197":"DE","198":"DE",
    "199":"DE","200":"DC","201":"VA","202":"DC","203":"DC","204":"DC","205":"DC","206":"MD",
    "207":"MD","208":"MD","209":"MD","210":"MD","211":"MD","212":"MD","214":"MD","215":"MD",
    "216":"MD","217":"WV","218":"WV","219":"WV","220":"VA","221":"VA","222":"VA","223":"VA",
    "224":"VA","225":"VA","226":"VA","227":"VA","228":"VA","229":"VA","230":"VA","231":"VA",
    "232":"VA","233":"VA","234":"VA","235":"VA","236":"VA","237":"VA","238":"VA","239":"VA",
    "240":"VA","241":"VA","242":"VA","243":"VA","244":"VA","245":"VA","246":"VA","247":"WV",
    "248":"WV","249":"WV","250":"WV","251":"WV","252":"WV","253":"WV","254":"WV","255":"WV",
    "256":"WV","257":"WV","258":"WV","259":"WV","260":"WV","261":"WV","262":"WV","263":"WV",
    "264":"WV","265":"WV","266":"WV","267":"WV","268":"WV","270":"NC","271":"NC","272":"NC",
    "273":"NC","274":"NC","275":"NC","276":"NC","277":"NC","278":"NC","279":"NC","280":"NC",
    "281":"NC","282":"NC","283":"NC","284":"NC","285":"NC","286":"NC","287":"NC","288":"NC",
    "289":"NC","290":"SC","291":"SC","292":"SC","293":"SC","294":"SC","295":"SC","296":"SC",
    "297":"SC","298":"SC","299":"SC","300":"GA","301":"GA","302":"GA","303":"GA","304":"GA",
    "305":"FL","306":"FL","307":"FL","308":"FL","309":"FL","310":"GA","311":"GA","312":"GA",
    "313":"GA","314":"GA","315":"GA","316":"GA","317":"GA","318":"GA","319":"GA","320":"FL",
    "321":"FL","322":"FL","323":"FL","324":"FL","325":"FL","326":"FL","327":"FL","328":"FL",
    "329":"FL","330":"FL","331":"FL","332":"FL","333":"FL","334":"FL","335":"FL","336":"FL",
    "337":"FL","338":"FL","339":"FL","340":"AA","341":"FL","342":"FL","344":"FL","346":"FL",
    "347":"FL","349":"FL","350":"AL","351":"AL","352":"AL","354":"AL","355":"AL","356":"AL",
    "357":"AL","358":"AL","359":"AL","360":"AL","361":"AL","362":"AL","363":"AL","364":"AL",
    "365":"AL","366":"AL","367":"AL","368":"AL","369":"MS","370":"TN","371":"TN","372":"TN",
    "373":"TN","374":"TN","376":"TN","377":"TN","378":"TN","379":"TN","380":"TN","381":"TN",
    "382":"TN","383":"TN","384":"TN","385":"TN","386":"MS","387":"MS","388":"MS","389":"MS",
    "390":"MS","391":"MS","392":"MS","393":"MS","394":"MS","395":"MS","396":"MS","397":"MS",
    "398":"GA","399":"GA","400":"KY","401":"KY","402":"KY","403":"KY","404":"KY","405":"KY",
    "406":"KY","407":"KY","408":"KY","409":"KY","410":"KY","411":"KY","412":"KY","413":"KY",
    "414":"KY","415":"KY","416":"KY","417":"KY","418":"KY","420":"KY","421":"KY","422":"KY",
    "423":"KY","424":"KY","425":"KY","426":"KY","427":"KY","430":"OH","431":"OH","432":"OH",
    "433":"OH","434":"OH","435":"OH","436":"OH","437":"OH","438":"OH","439":"OH","440":"OH",
    "441":"OH","442":"OH","443":"OH","444":"OH","445":"OH","446":"OH","447":"OH","448":"OH",
    "449":"OH","450":"OH","451":"OH","452":"OH","453":"OH","454":"OH","455":"OH","456":"OH",
    "457":"OH","458":"OH","460":"IN","461":"IN","462":"IN","463":"IN","464":"IN","465":"IN",
    "466":"IN","467":"IN","468":"IN","469":"IN","470":"IN","471":"IN","472":"IN","473":"IN",
    "474":"IN","475":"IN","476":"IN","477":"IN","478":"IN","479":"IN","480":"MI","481":"MI",
    "482":"MI","483":"MI","484":"MI","485":"MI","486":"MI","487":"MI","488":"MI","489":"MI",
    "490":"MI","491":"MI","492":"MI","493":"MI","494":"MI","495":"MI","496":"MI","497":"MI",
    "498":"MI","499":"MI","500":"IA","501":"IA","502":"IA","503":"IA","504":"IA","505":"IA",
    "506":"IA","507":"IA","508":"IA","509":"IA","510":"IA","511":"IA","512":"IA","513":"IA",
    "514":"IA","515":"IA","516":"IA","520":"IA","521":"IA","522":"IA","523":"IA","524":"IA",
    "525":"IA","526":"IA","527":"IA","528":"IA","530":"WI","531":"WI","532":"WI","534":"WI",
    "535":"WI","537":"WI","538":"WI","539":"WI","540":"WI","541":"WI","542":"WI","543":"WI",
    "544":"WI","545":"WI","546":"WI","547":"WI","548":"WI","549":"WI","550":"MN","551":"MN",
    "553":"MN","554":"MN","556":"MN","557":"MN","558":"MN","559":"MN","560":"MN","561":"MN",
    "562":"MN","563":"MN","564":"MN","565":"MN","566":"MN","567":"MN","570":"SD","571":"SD",
    "572":"SD","573":"SD","574":"SD","575":"SD","576":"SD","577":"SD","580":"ND","581":"ND",
    "582":"ND","583":"ND","584":"ND","585":"ND","586":"ND","587":"ND","588":"ND","590":"MT",
    "591":"MT","592":"MT","593":"MT","594":"MT","595":"MT","596":"MT","597":"MT","598":"MT",
    "599":"MT","600":"IL","601":"IL","602":"IL","603":"IL","604":"IL","605":"IL","606":"IL",
    "607":"IL","608":"IL","609":"IL","610":"IL","611":"IL","612":"IL","613":"IL","614":"IL",
    "615":"IL","616":"IL","617":"IL","618":"IL","619":"IL","620":"IL","622":"IL","623":"IL",
    "624":"IL","625":"IL","626":"IL","627":"IL","628":"IL","629":"IL","630":"MO","631":"MO",
    "633":"MO","634":"MO","635":"MO","636":"MO","637":"MO","638":"MO","639":"MO","640":"MO",
    "641":"MO","644":"MO","645":"MO","646":"MO","647":"MO","648":"MO","650":"MO","651":"MO",
    "652":"MO","653":"MO","654":"MO","655":"MO","656":"MO","657":"MO","658":"MO","660":"KS",
    "661":"KS","662":"KS","664":"KS","665":"KS","666":"KS","667":"KS","668":"KS","669":"KS",
    "670":"KS","671":"KS","672":"KS","673":"KS","674":"KS","675":"KS","676":"KS","677":"KS",
    "678":"KS","679":"KS","680":"NE","681":"NE","683":"NE","684":"NE","685":"NE","686":"NE",
    "687":"NE","688":"NE","689":"NE","690":"NE","691":"NE","692":"NE","693":"NE","700":"LA",
    "701":"LA","703":"LA","704":"LA","705":"LA","706":"LA","707":"LA","708":"LA","710":"LA",
    "711":"LA","712":"LA","713":"LA","714":"LA","716":"AR","717":"AR","718":"AR","719":"AR",
    "720":"AR","721":"AR","722":"AR","723":"AR","724":"AR","725":"AR","726":"AR","727":"AR",
    "728":"AR","729":"AR","730":"OK","731":"OK","733":"TX","734":"OK","735":"OK","736":"OK",
    "737":"TX","738":"OK","739":"OK","740":"OK","741":"OK","743":"OK","744":"OK","745":"OK",
    "746":"OK","747":"OK","748":"OK","749":"OK","750":"TX","751":"TX","752":"TX","753":"TX",
    "754":"TX","755":"TX","756":"TX","757":"TX","758":"TX","759":"TX","760":"TX","761":"TX",
    "762":"TX","763":"TX","764":"TX","765":"TX","766":"TX","767":"TX","768":"TX","769":"TX",
    "770":"TX","771":"TX","772":"TX","773":"TX","774":"TX","775":"TX","776":"TX","777":"TX",
    "778":"TX","779":"TX","780":"TX","781":"TX","782":"TX","783":"TX","784":"TX","785":"TX",
    "786":"TX","787":"TX","788":"TX","789":"TX","790":"TX","791":"TX","792":"TX","793":"TX",
    "794":"TX","795":"TX","796":"TX","797":"TX","798":"TX","799":"TX","800":"CO","801":"CO",
    "802":"CO","803":"CO","804":"CO","805":"CO","806":"CO","807":"CO","808":"CO","809":"CO",
    "810":"CO","811":"CO","812":"CO","813":"CO","814":"CO","815":"CO","816":"CO","820":"WY",
    "821":"WY","822":"WY","823":"WY","824":"WY","825":"WY","826":"WY","827":"WY","828":"WY",
    "829":"WY","830":"WY","831":"WY","832":"ID","833":"ID","834":"ID","835":"ID","836":"ID",
    "837":"ID","838":"ID","840":"UT","841":"UT","842":"UT","843":"UT","844":"UT","845":"UT",
    "846":"UT","847":"UT","850":"AZ","851":"AZ","852":"AZ","853":"AZ","855":"AZ","856":"AZ",
    "857":"AZ","859":"AZ","860":"AZ","863":"AZ","864":"AZ","865":"AZ","870":"NM","871":"NM",
    "873":"NM","874":"NM","875":"NM","877":"NM","878":"NM","879":"NM","880":"TX","881":"TX",
    "882":"TX","883":"TX","884":"TX","885":"TX","890":"NV","891":"NV","893":"NV","894":"NV",
    "895":"NV","897":"NV","898":"NV","900":"CA","901":"CA","902":"CA","903":"CA","904":"CA",
    "905":"CA","906":"CA","907":"CA","908":"CA","910":"CA","911":"CA","912":"CA","913":"CA",
    "914":"CA","915":"CA","916":"CA","917":"CA","918":"CA","919":"CA","920":"CA","921":"CA",
    "922":"CA","923":"CA","924":"CA","925":"CA","926":"CA","927":"CA","928":"CA","930":"CA",
    "931":"CA","932":"CA","933":"CA","934":"CA","935":"CA","936":"CA","937":"CA","938":"CA",
    "939":"CA","940":"CA","941":"CA","942":"CA","943":"CA","944":"CA","945":"CA","946":"CA",
    "947":"CA","948":"CA","949":"CA","950":"CA","951":"CA","952":"CA","953":"CA","954":"CA",
    "955":"CA","956":"CA","957":"CA","958":"CA","959":"CA","960":"CA","961":"CA","967":"HI",
    "968":"HI","970":"OR","971":"OR","972":"OR","973":"OR","974":"OR","975":"OR","976":"OR",
    "977":"OR","978":"OR","979":"OR","980":"WA","981":"WA","982":"WA","983":"WA","984":"WA",
    "985":"WA","986":"WA","988":"WA","989":"WA","990":"WA","991":"WA","992":"WA","993":"WA",
    "994":"WA","995":"AK","996":"AK","997":"AK","998":"AK","999":"AK"
}


def zip_to_state(zip_code):
    """Convert zip code to state abbreviation."""
    prefix = str(zip_code).strip()[:3]
    return ZIP_TO_STATE.get(prefix)


# ─── Supply-Side Water Damage Claims Data (per state) ───
# claims_per_1000: annual supply-side water damage claims per 1,000 insured homes
# avg_claim_cost: average cost per supply-side water damage claim ($)
# pipe_burst_pct: % of claims from pipe burst/freeze
# supply_line_pct: % from appliance supply line failures
# water_heater_pct: % from water heater failures
# slow_leak_pct: % from slow/hidden leaks
# prv_failure_pct: % from PRV/pressure-related failures
STATE_CLAIMS_DATA = {
    "AL":{"claims_per_1000":19.2,"avg_claim_cost":11800,"pipe_burst_pct":18,"supply_line_pct":28,"water_heater_pct":15,"slow_leak_pct":27,"prv_failure_pct":12},
    "AK":{"claims_per_1000":28.4,"avg_claim_cost":16200,"pipe_burst_pct":42,"supply_line_pct":18,"water_heater_pct":12,"slow_leak_pct":20,"prv_failure_pct":8},
    "AZ":{"claims_per_1000":16.8,"avg_claim_cost":12400,"pipe_burst_pct":8,"supply_line_pct":24,"water_heater_pct":22,"slow_leak_pct":30,"prv_failure_pct":16},
    "AR":{"claims_per_1000":20.1,"avg_claim_cost":11200,"pipe_burst_pct":22,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":25,"prv_failure_pct":11},
    "CA":{"claims_per_1000":15.4,"avg_claim_cost":18600,"pipe_burst_pct":6,"supply_line_pct":26,"water_heater_pct":20,"slow_leak_pct":32,"prv_failure_pct":16},
    "CO":{"claims_per_1000":22.6,"avg_claim_cost":14800,"pipe_burst_pct":32,"supply_line_pct":22,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":10},
    "CT":{"claims_per_1000":21.8,"avg_claim_cost":15200,"pipe_burst_pct":30,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":10},
    "DE":{"claims_per_1000":18.4,"avg_claim_cost":13600,"pipe_burst_pct":22,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":26,"prv_failure_pct":10},
    "DC":{"claims_per_1000":24.2,"avg_claim_cost":19800,"pipe_burst_pct":28,"supply_line_pct":24,"water_heater_pct":12,"slow_leak_pct":28,"prv_failure_pct":8},
    "FL":{"claims_per_1000":23.8,"avg_claim_cost":16400,"pipe_burst_pct":4,"supply_line_pct":30,"water_heater_pct":18,"slow_leak_pct":34,"prv_failure_pct":14},
    "GA":{"claims_per_1000":18.6,"avg_claim_cost":12800,"pipe_burst_pct":14,"supply_line_pct":28,"water_heater_pct":18,"slow_leak_pct":28,"prv_failure_pct":12},
    "HI":{"claims_per_1000":12.4,"avg_claim_cost":14200,"pipe_burst_pct":2,"supply_line_pct":30,"water_heater_pct":20,"slow_leak_pct":35,"prv_failure_pct":13},
    "ID":{"claims_per_1000":20.8,"avg_claim_cost":12600,"pipe_burst_pct":30,"supply_line_pct":24,"water_heater_pct":16,"slow_leak_pct":20,"prv_failure_pct":10},
    "IL":{"claims_per_1000":22.4,"avg_claim_cost":14200,"pipe_burst_pct":32,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":8},
    "IN":{"claims_per_1000":21.6,"avg_claim_cost":12800,"pipe_burst_pct":28,"supply_line_pct":26,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":10},
    "IA":{"claims_per_1000":23.2,"avg_claim_cost":12400,"pipe_burst_pct":34,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":20,"prv_failure_pct":8},
    "KS":{"claims_per_1000":21.4,"avg_claim_cost":11800,"pipe_burst_pct":26,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":22,"prv_failure_pct":10},
    "KY":{"claims_per_1000":20.2,"avg_claim_cost":11600,"pipe_burst_pct":24,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":24,"prv_failure_pct":10},
    "LA":{"claims_per_1000":22.8,"avg_claim_cost":13400,"pipe_burst_pct":10,"supply_line_pct":28,"water_heater_pct":18,"slow_leak_pct":30,"prv_failure_pct":14},
    "ME":{"claims_per_1000":24.6,"avg_claim_cost":13800,"pipe_burst_pct":38,"supply_line_pct":22,"water_heater_pct":12,"slow_leak_pct":20,"prv_failure_pct":8},
    "MD":{"claims_per_1000":19.8,"avg_claim_cost":14600,"pipe_burst_pct":24,"supply_line_pct":26,"water_heater_pct":14,"slow_leak_pct":26,"prv_failure_pct":10},
    "MA":{"claims_per_1000":23.4,"avg_claim_cost":16800,"pipe_burst_pct":34,"supply_line_pct":22,"water_heater_pct":12,"slow_leak_pct":24,"prv_failure_pct":8},
    "MI":{"claims_per_1000":22.8,"avg_claim_cost":13200,"pipe_burst_pct":32,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":8},
    "MN":{"claims_per_1000":25.6,"avg_claim_cost":14400,"pipe_burst_pct":38,"supply_line_pct":22,"water_heater_pct":12,"slow_leak_pct":20,"prv_failure_pct":8},
    "MS":{"claims_per_1000":19.4,"avg_claim_cost":10800,"pipe_burst_pct":14,"supply_line_pct":28,"water_heater_pct":18,"slow_leak_pct":28,"prv_failure_pct":12},
    "MO":{"claims_per_1000":21.2,"avg_claim_cost":12200,"pipe_burst_pct":26,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":22,"prv_failure_pct":10},
    "MT":{"claims_per_1000":24.2,"avg_claim_cost":13200,"pipe_burst_pct":36,"supply_line_pct":22,"water_heater_pct":14,"slow_leak_pct":20,"prv_failure_pct":8},
    "NE":{"claims_per_1000":22.8,"avg_claim_cost":12000,"pipe_burst_pct":32,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":8},
    "NV":{"claims_per_1000":17.2,"avg_claim_cost":14200,"pipe_burst_pct":10,"supply_line_pct":24,"water_heater_pct":22,"slow_leak_pct":28,"prv_failure_pct":16},
    "NH":{"claims_per_1000":24.8,"avg_claim_cost":14600,"pipe_burst_pct":36,"supply_line_pct":22,"water_heater_pct":12,"slow_leak_pct":22,"prv_failure_pct":8},
    "NJ":{"claims_per_1000":21.4,"avg_claim_cost":16200,"pipe_burst_pct":28,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":26,"prv_failure_pct":8},
    "NM":{"claims_per_1000":16.4,"avg_claim_cost":11800,"pipe_burst_pct":14,"supply_line_pct":26,"water_heater_pct":20,"slow_leak_pct":26,"prv_failure_pct":14},
    "NY":{"claims_per_1000":22.6,"avg_claim_cost":18200,"pipe_burst_pct":30,"supply_line_pct":24,"water_heater_pct":12,"slow_leak_pct":26,"prv_failure_pct":8},
    "NC":{"claims_per_1000":18.8,"avg_claim_cost":12600,"pipe_burst_pct":16,"supply_line_pct":28,"water_heater_pct":16,"slow_leak_pct":28,"prv_failure_pct":12},
    "ND":{"claims_per_1000":26.4,"avg_claim_cost":13600,"pipe_burst_pct":40,"supply_line_pct":20,"water_heater_pct":12,"slow_leak_pct":20,"prv_failure_pct":8},
    "OH":{"claims_per_1000":21.8,"avg_claim_cost":13000,"pipe_burst_pct":28,"supply_line_pct":26,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":10},
    "OK":{"claims_per_1000":20.6,"avg_claim_cost":11400,"pipe_burst_pct":20,"supply_line_pct":26,"water_heater_pct":18,"slow_leak_pct":24,"prv_failure_pct":12},
    "OR":{"claims_per_1000":17.8,"avg_claim_cost":14800,"pipe_burst_pct":18,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":28,"prv_failure_pct":12},
    "PA":{"claims_per_1000":22.2,"avg_claim_cost":14400,"pipe_burst_pct":30,"supply_line_pct":24,"water_heater_pct":14,"slow_leak_pct":24,"prv_failure_pct":8},
    "RI":{"claims_per_1000":22.4,"avg_claim_cost":15600,"pipe_burst_pct":32,"supply_line_pct":24,"water_heater_pct":12,"slow_leak_pct":24,"prv_failure_pct":8},
    "SC":{"claims_per_1000":18.2,"avg_claim_cost":12200,"pipe_burst_pct":12,"supply_line_pct":28,"water_heater_pct":18,"slow_leak_pct":30,"prv_failure_pct":12},
    "SD":{"claims_per_1000":24.8,"avg_claim_cost":12800,"pipe_burst_pct":36,"supply_line_pct":22,"water_heater_pct":14,"slow_leak_pct":20,"prv_failure_pct":8},
    "TN":{"claims_per_1000":19.6,"avg_claim_cost":12000,"pipe_burst_pct":18,"supply_line_pct":28,"water_heater_pct":16,"slow_leak_pct":26,"prv_failure_pct":12},
    "TX":{"claims_per_1000":24.2,"avg_claim_cost":15800,"pipe_burst_pct":16,"supply_line_pct":28,"water_heater_pct":18,"slow_leak_pct":26,"prv_failure_pct":12},
    "UT":{"claims_per_1000":19.4,"avg_claim_cost":13200,"pipe_burst_pct":22,"supply_line_pct":24,"water_heater_pct":18,"slow_leak_pct":24,"prv_failure_pct":12},
    "VT":{"claims_per_1000":25.2,"avg_claim_cost":14200,"pipe_burst_pct":38,"supply_line_pct":22,"water_heater_pct":12,"slow_leak_pct":20,"prv_failure_pct":8},
    "VA":{"claims_per_1000":19.2,"avg_claim_cost":13800,"pipe_burst_pct":20,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":28,"prv_failure_pct":10},
    "WA":{"claims_per_1000":18.6,"avg_claim_cost":15400,"pipe_burst_pct":16,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":30,"prv_failure_pct":12},
    "WV":{"claims_per_1000":21.4,"avg_claim_cost":11200,"pipe_burst_pct":26,"supply_line_pct":26,"water_heater_pct":16,"slow_leak_pct":22,"prv_failure_pct":10},
    "WI":{"claims_per_1000":24.4,"avg_claim_cost":13600,"pipe_burst_pct":34,"supply_line_pct":24,"water_heater_pct":12,"slow_leak_pct":22,"prv_failure_pct":8},
    "WY":{"claims_per_1000":23.8,"avg_claim_cost":12800,"pipe_burst_pct":34,"supply_line_pct":22,"water_heater_pct":14,"slow_leak_pct":22,"prv_failure_pct":8},
    "PR":{"claims_per_1000":14.6,"avg_claim_cost":9800,"pipe_burst_pct":4,"supply_line_pct":30,"water_heater_pct":20,"slow_leak_pct":32,"prv_failure_pct":14},
    "VI":{"claims_per_1000":13.8,"avg_claim_cost":10200,"pipe_burst_pct":2,"supply_line_pct":30,"water_heater_pct":22,"slow_leak_pct":34,"prv_failure_pct":12},
}


def get_claims_data(state):
    """Get supply-side water damage claims data for a state."""
    return STATE_CLAIMS_DATA.get(state)


def score_claims(claims_data):
    """Score claims risk 0-100 based on frequency and severity."""
    if not claims_data:
        return 50.0
    freq = claims_data.get("claims_per_1000", 18)
    cost = claims_data.get("avg_claim_cost", 13000)
    # Frequency score: national avg ~20/1000, scale 10-30 range
    freq_score = min(max((freq - 10) / 20 * 100, 0), 100)
    # Severity score: national avg ~$13K, scale $8K-$20K range
    cost_score = min(max((cost - 8000) / 12000 * 100, 0), 100)
    # Combined: 60% frequency, 40% severity
    return round(freq_score * 0.6 + cost_score * 0.4, 1)


def geocode_zip(zip_code):
    """Convert zip code to lat/lon using Open-Meteo Geocoding API."""
    try:
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": f"{zip_code} USA", "count": 1, "language": "en", "format": "json"},
            timeout=10
        )
        data = resp.json()
        if data.get("results"):
            r = data["results"][0]
            return r["latitude"], r["longitude"]
    except Exception:
        pass

    # Fallback: approximate centroids for major zip prefixes
    FALLBACK = {
        "FL": (28.0, -82.5), "TX": (31.0, -100.0), "CA": (36.7, -119.8),
        "AZ": (34.0, -111.9), "NY": (42.0, -75.5), "GA": (33.0, -83.5),
        "NC": (35.5, -79.5), "OH": (40.5, -82.5), "PA": (40.8, -77.8),
        "IL": (40.0, -89.0), "MI": (43.0, -84.5), "NJ": (40.0, -74.5),
    }
    state = zip_to_state(zip_code)
    if state and state in FALLBACK:
        return FALLBACK[state]
    return 39.8, -98.6  # US center


# ─── Climate Scoring ───

def fetch_climate_data(lat, lon):
    """Fetch 12-month climate data from Open-Meteo Archive API."""
    end = datetime.now()
    start = end - timedelta(days=365)
    try:
        resp = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat, "longitude": lon,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum",
                "temperature_unit": "fahrenheit",
                "precipitation_unit": "inch",
                "timezone": "America/New_York"
            },
            timeout=15
        )
        data = resp.json()
        daily = data.get("daily", {})
        mins = daily.get("temperature_2m_min", [])
        maxes = daily.get("temperature_2m_max", [])
        precip = daily.get("precipitation_sum", [])

        freeze_days = sum(1 for t in mins if t is not None and t < 32)
        heat_days = sum(1 for t in maxes if t is not None and t > 95)
        total_precip = sum(p for p in precip if p is not None)
        max_daily_precip = max((p for p in precip if p is not None), default=0)

        return {
            "freeze_days": freeze_days,
            "heat_days": heat_days,
            "total_precip_inches": round(total_precip, 1),
            "max_daily_precip_inches": round(max_daily_precip, 2),
            "data_points": len(mins)
        }
    except Exception as e:
        return {"error": str(e), "freeze_days": 0, "heat_days": 0,
                "total_precip_inches": 0, "max_daily_precip_inches": 0, "data_points": 0}


def score_climate(climate_data):
    """Score climate risk 0-100."""
    fd = climate_data.get("freeze_days", 0)
    hd = climate_data.get("heat_days", 0)
    tp = climate_data.get("total_precip_inches", 0)
    mp = climate_data.get("max_daily_precip_inches", 0)

    freeze_score = min(fd / 60 * 100, 100)
    heat_score = min(hd / 45 * 100, 100)
    precip_score = min(tp / 60 * 100, 100)
    extreme_precip = min(mp / 4 * 100, 100)

    return round(freeze_score * 0.35 + heat_score * 0.15 + precip_score * 0.25 + extreme_precip * 0.25, 1)


# ─── Water Quality Scoring ───

def get_water_quality(state):
    """Get water quality data for a state from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM water_quality WHERE state = ?", (state,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def score_water_quality(wq_data):
    """Score water quality risk 0-100."""
    if not wq_data:
        return 50.0  # Unknown = moderate risk
    return round(min(wq_data.get("composite_score", 50), 100), 1)


# ─── Infrastructure Scoring ───

def get_infrastructure(state):
    """Get housing/infrastructure age data for a state."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM housing_age WHERE state = ?", (state,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def score_infrastructure(infra_data):
    """Score infrastructure risk 0-100."""
    if not infra_data:
        return 50.0
    return round(min(infra_data.get("infrastructure_score", 50), 100), 1)


# ─── Pressure Scoring ───

def get_pressure_data(state):
    """Get city water pressure data for a state."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM city_pressure WHERE state = ?", (state,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def score_pressure(pressure_data):
    """Score pressure risk 0-100."""
    if not pressure_data:
        return 50.0
    return round(min(max(0, pressure_data.get("pressure_score", 50)), 100), 1)


# ─── Builder Quality Scoring ───

def search_builders(state=None, name=None, grade=None, limit=50):
    """Search builders in the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM builders WHERE 1=1"
    params = []
    if state:
        query += " AND state = ?"
        params.append(state)
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    query += f" ORDER BY composite_score DESC LIMIT {limit}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_builder_score(state):
    """Get average builder quality score for a state."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT AVG(composite_score) as avg_score, COUNT(*) as count FROM builders WHERE state = ?",
        (state,)
    ).fetchone()
    conn.close()
    if row and row['count'] > 0:
        return {"avg_score": round(row['avg_score'], 1), "builder_count": row['count']}
    return {"avg_score": 50.0, "builder_count": 0}


def score_builder(state):
    """Score builder quality risk 0-100 (inverted: low builder quality = high risk)."""
    bs = get_builder_score(state)
    # Invert: high builder score = low risk
    return round(max(0, 100 - bs["avg_score"]), 1)


def compute_builder_score(builder_data):
    """
    Compute builder composite score and grade from actual data fields.
    Returns (composite_score, grade) tuple.

    Uses normalized metrics (per 1,000 homes) instead of raw counts,
    so a builder with 50 complaints and 50,000 homes isn't penalized
    the same as one with 50 complaints and 2,000 homes.
    """
    homes = max(builder_data.get("homes_built", 1000), 100)  # floor at 100 to avoid division issues

    # ── Component 1: Quality indicators average (30%) ──
    callback = builder_data.get("callback_rate", 70) or 70
    plumbing_mat = builder_data.get("plumbing_material_score", 70) or 70
    drainage = builder_data.get("drainage_score", 70) or 70
    quality_avg = (callback + plumbing_mat + drainage) / 3.0

    # ── Component 2: Warranty claim rate (25%) ──
    # Direct percentage — lower is better
    wcr = builder_data.get("warranty_claim_rate", 3.0) or 3.0
    if wcr <= 0.8:
        warranty_score = 100
    elif wcr <= 1.5:
        warranty_score = 90 - (wcr - 0.8) * 14.3
    elif wcr <= 2.5:
        warranty_score = 80 - (wcr - 1.5) * 15
    elif wcr <= 3.5:
        warranty_score = 65 - (wcr - 2.5) * 15
    elif wcr <= 5.0:
        warranty_score = 50 - (wcr - 3.5) * 16.7
    elif wcr <= 7.0:
        warranty_score = 25 - (wcr - 5.0) * 10
    else:
        warranty_score = max(0, 5 - (wcr - 7.0) * 2.5)

    # ── Component 3: Complaints per 1,000 homes (20%) ──
    raw_complaints = builder_data.get("bbb_complaints", 0) or 0
    complaints_per_1k = (raw_complaints / homes) * 1000
    if complaints_per_1k <= 0.5:
        complaint_score = 100
    elif complaints_per_1k <= 1.5:
        complaint_score = 90 - (complaints_per_1k - 0.5) * 15
    elif complaints_per_1k <= 3.0:
        complaint_score = 75 - (complaints_per_1k - 1.5) * 16.7
    elif complaints_per_1k <= 5.0:
        complaint_score = 50 - (complaints_per_1k - 3.0) * 15
    elif complaints_per_1k <= 8.0:
        complaint_score = 20 - (complaints_per_1k - 5.0) * 5
    else:
        complaint_score = max(0, 5 - (complaints_per_1k - 8.0) * 2.5)

    # ── Component 4: Violations per 1,000 homes (15%) ──
    raw_violations = builder_data.get("building_dept_violations", 0) or 0
    violations_per_1k = (raw_violations / homes) * 1000
    if violations_per_1k <= 0.1:
        violation_score = 100
    elif violations_per_1k <= 0.5:
        violation_score = 90 - (violations_per_1k - 0.1) * 25
    elif violations_per_1k <= 1.0:
        violation_score = 80 - (violations_per_1k - 0.5) * 30
    elif violations_per_1k <= 2.0:
        violation_score = 65 - (violations_per_1k - 1.0) * 25
    elif violations_per_1k <= 3.0:
        violation_score = 40 - (violations_per_1k - 2.0) * 20
    else:
        violation_score = max(0, 20 - (violations_per_1k - 3.0) * 10)

    # ── Component 5: Plumbing sub quality (10%) ──
    psq = builder_data.get("plumbing_sub_quality", "unknown") or "unknown"
    psq_map = {"premium": 90, "mid-tier": 55, "budget": 20, "unknown": 45}
    plumbing_quality_score = psq_map.get(psq, 45)

    # ── Weighted composite ──
    composite = (
        quality_avg * 0.30 +
        warranty_score * 0.25 +
        complaint_score * 0.20 +
        violation_score * 0.15 +
        plumbing_quality_score * 0.10
    )

    # ── License status penalty ──
    license_status = builder_data.get("license_status", "active") or "active"
    if license_status == "probation":
        composite -= 15
    elif license_status == "suspended":
        composite -= 30
    elif license_status == "revoked":
        composite = min(composite, 15)

    composite = round(max(0, min(100, composite)), 1)

    # ── Grade assignment ──
    if composite >= 82:
        grade = "A"
    elif composite >= 67:
        grade = "B"
    elif composite >= 52:
        grade = "C"
    elif composite >= 38:
        grade = "D"
    else:
        grade = "F"

    return composite, grade


# ─── Regulatory Scoring ───

def get_regulatory(state):
    """Get regulatory/mandate data for a state."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM regulatory WHERE state = ?", (state,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def score_regulatory(reg_data):
    """Score regulatory risk 0-100 (fewer mandates = higher risk)."""
    if not reg_data:
        return 60.0  # No data = moderate-high risk
    return round(min(max(0, reg_data.get("compliance_score", 60)), 100), 1)


# ─── Composite Scoring ───

def compute_composite_score(zip_code, builder_name=None):
    """
    Compute full composite risk score for a zip code.
    Returns detailed breakdown across all 7 layers.
    """
    state = zip_to_state(zip_code)
    if not state:
        return {"error": f"Could not resolve state for zip code {zip_code}"}

    lat, lon = geocode_zip(zip_code)

    # Layer 1: Climate
    climate_data = fetch_climate_data(lat, lon)
    climate_score = score_climate(climate_data)

    # Layer 2: Water Quality
    wq_data = get_water_quality(state)
    wq_score = score_water_quality(wq_data)

    # Layer 3: Infrastructure
    infra_data = get_infrastructure(state)
    infra_score = score_infrastructure(infra_data)

    # Layer 4: Pressure
    pressure_data = get_pressure_data(state)
    pressure_score = score_pressure(pressure_data)

    # Layer 5: Builder Quality
    builder_data = get_builder_score(state)
    builder_risk_score = score_builder(state)

    # Layer 6: Regulatory
    reg_data = get_regulatory(state)
    reg_score = score_regulatory(reg_data)

    # Layer 7: Claims History
    claims_data = get_claims_data(state)
    claims_score = score_claims(claims_data)

    # Composite: Claims 20% + Climate 15% + WQ 15% + Infrastructure 15% + Pressure 15% + Builder 10% + Regulatory 10%
    composite = round(
        claims_score * 0.20 +
        climate_score * 0.15 +
        wq_score * 0.15 +
        infra_score * 0.15 +
        pressure_score * 0.15 +
        builder_risk_score * 0.10 +
        reg_score * 0.10,
        1
    )

    # Risk level
    if composite <= 30:
        risk_level = "Low"
        risk_color = "#22c55e"
    elif composite <= 60:
        risk_level = "Moderate"
        risk_color = "#f59e0b"
    elif composite <= 80:
        risk_level = "High"
        risk_color = "#f97316"
    else:
        risk_level = "Critical"
        risk_color = "#ef4444"

    return {
        "zip_code": zip_code,
        "state": state,
        "latitude": lat,
        "longitude": lon,
        "composite_score": composite,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "scored_at": datetime.utcnow().isoformat(),
        "layers": {
            "climate": {
                "score": climate_score,
                "data": climate_data
            },
            "water_quality": {
                "score": wq_score,
                "data": wq_data or {"note": "No state-level data available"}
            },
            "infrastructure": {
                "score": infra_score,
                "data": infra_data or {"note": "No state-level data available"}
            },
            "pressure": {
                "score": pressure_score,
                "data": pressure_data or {"note": "No state-level data available"}
            },
            "builder_quality": {
                "score": builder_risk_score,
                "data": builder_data
            },
            "regulatory": {
                "score": reg_score,
                "data": reg_data or {"note": "No state-level data available"}
            },
            "claims": {
                "score": claims_score,
                "data": claims_data or {"note": "No state-level data available"}
            }
        },
        "device_enhanced": False,
        "confidence": "Moderate (public data only)",
        "namara_gap": [
            "Real-time water pressure monitoring (20-sec intervals)",
            "Small and large leak detection with auto shut-off",
            "Freeze protection with in-pipe temperature monitoring",
            "Thermal expansion relief",
            "Supply-side pressure relief and optimization"
        ]
    }


# ─── Property-Level Scoring ───

PIPE_MATERIAL_FROM_YEAR = [
    (1940, "lead/galvanized", 95),
    (1960, "galvanized", 80),
    (1975, "copper/galvanized", 55),
    (1990, "copper", 35),
    (2000, "copper/cpvc", 25),
    (2010, "pex/cpvc", 15),
    (2030, "pex", 10),
]

PIPE_RISK_SCORES = {
    "lead": 98, "lead/galvanized": 95, "galvanized": 80, "copper/galvanized": 55,
    "copper": 35, "copper/cpvc": 25, "cpvc": 22, "pex/cpvc": 15, "pex": 10,
    "unknown": 50,
}


def estimate_pipe_material(year_built):
    """Estimate pipe material from year built."""
    if not year_built:
        return "unknown", 50
    for threshold, material, risk in PIPE_MATERIAL_FROM_YEAR:
        if year_built <= threshold:
            return material, risk
    return "pex", 10


def lookup_property(address, city, state, zip_code):
    """Look up a property in the database. Returns dict or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = None
    addr = address.strip()
    st = state.strip() if state else ""
    zc = str(zip_code).strip() if zip_code else ""

    # Try exact address + state match first
    if st:
        row = conn.execute(
            "SELECT * FROM properties WHERE LOWER(address) = LOWER(?) AND LOWER(state) = LOWER(?)",
            (addr, st)
        ).fetchone()
    # Try exact address + zip match
    if not row and zc:
        row = conn.execute(
            "SELECT * FROM properties WHERE LOWER(address) = LOWER(?) AND zip_code = ?",
            (addr, zc)
        ).fetchone()
    # Partial address + state
    if not row and st:
        row = conn.execute(
            "SELECT * FROM properties WHERE LOWER(address) LIKE ? AND LOWER(state) = LOWER(?)",
            (f"%{addr.lower()}%", st)
        ).fetchone()
    # Partial address + zip
    if not row and zc:
        row = conn.execute(
            "SELECT * FROM properties WHERE LOWER(address) LIKE ? AND zip_code = ?",
            (f"%{addr.lower()}%", zc)
        ).fetchone()
    conn.close()
    return dict(row) if row else None


def lookup_builder_by_id(builder_id):
    """Look up a specific builder by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM builders WHERE id = ?", (builder_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def lookup_builder_by_name(name, state=None):
    """Look up a builder by name (fuzzy match)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if state:
        row = conn.execute(
            "SELECT * FROM builders WHERE LOWER(name) LIKE ? AND state = ? ORDER BY composite_score DESC LIMIT 1",
            (f"%{name.lower()}%", state)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM builders WHERE LOWER(name) LIKE ? ORDER BY composite_score DESC LIMIT 1",
            (f"%{name.lower()}%",)
        ).fetchone()
    conn.close()
    return dict(row) if row else None


def score_property_age(year_built):
    """Score home age risk 0-100. Older homes = higher risk."""
    if not year_built:
        return 50.0
    age = datetime.now().year - year_built
    if age <= 5:
        return 8.0
    elif age <= 10:
        return 15.0
    elif age <= 20:
        return 28.0
    elif age <= 30:
        return 42.0
    elif age <= 40:
        return 58.0
    elif age <= 50:
        return 72.0
    elif age <= 65:
        return 82.0
    else:
        return 92.0


def score_pipe_material(pipe_material, year_built):
    """Score pipe material risk 0-100."""
    if pipe_material and pipe_material.lower() != "unknown":
        return PIPE_RISK_SCORES.get(pipe_material.lower(), 50)
    # Estimate from year built
    _, risk = estimate_pipe_material(year_built)
    return risk


def score_water_heater_risk(age_years, heater_type="tank"):
    """Score water heater failure risk 0-100."""
    if age_years is None:
        return 40.0
    # Tank heaters: avg lifespan 8-12 years, tankless: 15-20 years
    if heater_type == "tankless":
        if age_years <= 5:
            return 8.0
        elif age_years <= 10:
            return 18.0
        elif age_years <= 15:
            return 35.0
        elif age_years <= 20:
            return 60.0
        else:
            return 85.0
    else:  # tank
        if age_years <= 3:
            return 8.0
        elif age_years <= 6:
            return 18.0
        elif age_years <= 8:
            return 35.0
        elif age_years <= 10:
            return 55.0
        elif age_years <= 12:
            return 75.0
        else:
            return 92.0


def score_permit_history(total_permits, last_permit_year, year_built):
    """Score plumbing maintenance risk. More recent permits = lower risk (maintained home)."""
    if not year_built:
        return 50.0
    age = datetime.now().year - year_built
    if age <= 5:
        return 10.0  # New home, no permits needed yet

    if total_permits == 0 and age > 20:
        return 78.0  # Old home, never maintained
    elif total_permits == 0 and age > 10:
        return 55.0

    if last_permit_year:
        years_since = datetime.now().year - last_permit_year
        if years_since <= 3:
            return 12.0
        elif years_since <= 7:
            return 25.0
        elif years_since <= 15:
            return 40.0
        else:
            return 60.0
    return 45.0


def score_prior_claims(num_claims, total_cost):
    """Score prior claims risk 0-100. Properties with history are higher risk."""
    if num_claims == 0:
        return 10.0
    elif num_claims == 1:
        base = 40.0
    elif num_claims == 2:
        base = 60.0
    elif num_claims == 3:
        base = 75.0
    else:
        base = 88.0
    # Adjust for severity
    if total_cost and total_cost > 50000:
        base = min(base + 10, 100)
    elif total_cost and total_cost > 25000:
        base = min(base + 5, 100)
    return base


def score_protection_devices(has_prv, has_expansion_tank):
    """Score protection level. Devices present = lower risk."""
    if has_prv and has_expansion_tank:
        return 10.0
    elif has_prv:
        return 30.0
    elif has_expansion_tank:
        return 45.0
    else:
        return 70.0


def score_individual_builder(builder):
    """Score a specific builder's quality 0-100 (higher = more risk)."""
    if not builder:
        return 50.0, {}

    factors = {}

    # Core construction quality score (inverted: high quality = low risk)
    core_score = builder.get("composite_score", 50)
    factors["construction_quality"] = round(100 - core_score, 1)

    # BBB rating
    bbb_map = {"A+": 5, "A": 10, "A-": 18, "B+": 28, "B": 38, "B-": 48,
               "C+": 58, "C": 65, "C-": 72, "D+": 78, "D": 85, "D-": 90, "F": 95, "NR": 45}
    bbb_rating = builder.get("bbb_rating", "NR")
    factors["bbb_rating_risk"] = bbb_map.get(bbb_rating, 45)

    # BBB complaints
    complaints = builder.get("bbb_complaints", 0)
    if complaints == 0:
        factors["bbb_complaints_risk"] = 10
    elif complaints <= 3:
        factors["bbb_complaints_risk"] = 25
    elif complaints <= 8:
        factors["bbb_complaints_risk"] = 45
    elif complaints <= 15:
        factors["bbb_complaints_risk"] = 65
    else:
        factors["bbb_complaints_risk"] = 85

    # License status
    license_status = builder.get("license_status", "unknown")
    license_map = {"active": 10, "conditional": 45, "probation": 70, "expired": 85,
                   "suspended": 95, "revoked": 98, "unknown": 50}
    factors["license_risk"] = license_map.get(license_status, 50)

    # Building dept violations
    violations = builder.get("building_dept_violations", 0)
    if violations == 0:
        factors["violation_risk"] = 8
    elif violations <= 2:
        factors["violation_risk"] = 28
    elif violations <= 5:
        factors["violation_risk"] = 50
    elif violations <= 10:
        factors["violation_risk"] = 72
    else:
        factors["violation_risk"] = 90

    # Warranty claim rate
    warranty = builder.get("warranty_claim_rate", 0)
    factors["warranty_risk"] = min(round(warranty / 0.15 * 100, 1), 100) if warranty else 40

    # Plumbing sub quality
    sub_map = {"excellent": 8, "good": 22, "average": 45, "below_average": 68, "poor": 88, "unknown": 50}
    factors["plumbing_sub_risk"] = sub_map.get(builder.get("plumbing_sub_quality", "unknown"), 50)

    # Weighted composite for builder
    builder_risk = round(
        factors["construction_quality"] * 0.25 +
        factors["bbb_rating_risk"] * 0.15 +
        factors["bbb_complaints_risk"] * 0.10 +
        factors["license_risk"] * 0.15 +
        factors["violation_risk"] * 0.15 +
        factors["warranty_risk"] * 0.10 +
        factors["plumbing_sub_risk"] * 0.10,
        1
    )

    return builder_risk, factors


def compute_property_score(address, city, state, zip_code,
                            year_built=None, pipe_material=None,
                            builder_name=None, builder_id=None,
                            water_heater_age=None, water_heater_type="tank",
                            has_prv=False, has_expansion_tank=False,
                            prior_claims=0, prior_claim_cost=0,
                            total_permits=0, last_permit_year=None,
                            sqft=None, stories=None, bathrooms=None):
    """
    Compute address-level property risk score.
    Combines property-specific factors (~60%) with environmental context (~40%).
    Returns detailed breakdown for all factors.
    """
    if not state:
        state = zip_to_state(zip_code)
    if not state:
        return {"error": f"Could not resolve state for zip code {zip_code}"}

    # ─── Data Enrichment (3-tier priority: user input > local DB > external API) ───

    # Tier 1: User-provided values are already in function params (highest priority)

    # Track data source for each field: "user" > "db" > "attom" > "default"
    data_sources = {}

    # Tier 2: Local database lookup — fills gaps left by user input
    db_property = lookup_property(address, city, state, zip_code)
    if db_property:
        if year_built is None and db_property.get("year_built"):
            year_built = db_property["year_built"]
            data_sources["year_built"] = "db"
        if not pipe_material and db_property.get("pipe_material"):
            pipe_material = db_property["pipe_material"]
            data_sources["pipe_material"] = "db"
        if not builder_id and db_property.get("builder_id"):
            builder_id = db_property["builder_id"]
        if not builder_name and db_property.get("builder_name"):
            builder_name = db_property["builder_name"]
        if water_heater_age is None and db_property.get("water_heater_age_years") is not None:
            water_heater_age = db_property["water_heater_age_years"]
        water_heater_type = water_heater_type or db_property.get("water_heater_type", "tank")
        has_prv = has_prv or bool(db_property.get("has_prv"))
        has_expansion_tank = has_expansion_tank or bool(db_property.get("has_expansion_tank"))
        prior_claims = prior_claims or db_property.get("prior_water_claims", 0)
        prior_claim_cost = prior_claim_cost or db_property.get("prior_claim_total_cost", 0)
        total_permits = total_permits or db_property.get("total_plumbing_permits", 0)
        last_permit_year = last_permit_year or db_property.get("last_plumbing_permit_year")
        if sqft is None and db_property.get("sqft"):
            sqft = db_property["sqft"]
            data_sources["sqft"] = "db"
        if stories is None and db_property.get("stories") is not None:
            stories = db_property["stories"]
            data_sources["stories"] = "db"
        if bathrooms is None and db_property.get("bathrooms") is not None:
            bathrooms = db_property["bathrooms"]
            data_sources["bathrooms"] = "db"

    # Mark user-provided fields (anything set before DB lookup)
    if year_built is not None and "year_built" not in data_sources:
        data_sources["year_built"] = "user"
    if sqft is not None and "sqft" not in data_sources:
        data_sources["sqft"] = "user"
    if stories is not None and "stories" not in data_sources:
        data_sources["stories"] = "user"
    if bathrooms is not None and "bathrooms" not in data_sources:
        data_sources["bathrooms"] = "user"

    # Tier 3: External property data API (ATTOM) — fills remaining gaps ONLY
    enrichment_data = None
    enrichment_source = None
    try:
        from property_enrichment import enrich_property
        enrichment_data = enrich_property(address, city, state, zip_code)
        if enrichment_data:
            enrichment_source = enrichment_data.get("provider", "external")
            logger.info(f"Property enrichment from {enrichment_source}: {list(enrichment_data.keys())}")
            # Only fill in fields that are still None after user input + DB
            if year_built is None and enrichment_data.get("year_built"):
                year_built = enrichment_data["year_built"]
                data_sources["year_built"] = "attom"
            if sqft is None and enrichment_data.get("sqft"):
                sqft = enrichment_data["sqft"]
                data_sources["sqft"] = "attom"
            if stories is None and enrichment_data.get("stories") is not None:
                stories = enrichment_data["stories"]
                data_sources["stories"] = "attom"
            if bathrooms is None and enrichment_data.get("bathrooms") is not None:
                bathrooms = enrichment_data["bathrooms"]
                data_sources["bathrooms"] = "attom"
    except ImportError:
        logger.debug("Property enrichment module not available")
    except Exception as e:
        logger.warning(f"Property enrichment failed: {e}")

    # Apply defaults for any fields still None (display only, not used in scoring)
    if stories is None:
        stories = 1
    if bathrooms is None:
        bathrooms = 2.0

    # Estimate pipe material if not provided
    pipe_source = "provided"
    if not pipe_material or pipe_material.lower() == "unknown":
        pipe_material, _ = estimate_pipe_material(year_built)
        pipe_source = "estimated_from_year"

    # ─── Property-Level Factors (60% of total) ───

    # 1. Home age (15%)
    age_score = score_property_age(year_built)

    # 2. Pipe material (15%)
    pipe_score = score_pipe_material(pipe_material, year_built)

    # 3. Water heater (10%)
    heater_score = score_water_heater_risk(water_heater_age, water_heater_type)

    # 4. Plumbing permit/maintenance history (8%)
    permit_score = score_permit_history(total_permits, last_permit_year, year_built)

    # 5. Prior claims (7%)
    claims_history_score = score_prior_claims(prior_claims, prior_claim_cost)

    # 6. Protection devices (5%)
    protection_score = score_protection_devices(has_prv, has_expansion_tank)

    # 7. Builder quality — specific builder if available (property-level), else state avg
    builder = None
    builder_risk = 50.0
    builder_factors = {}
    if builder_id:
        builder = lookup_builder_by_id(builder_id)
    elif builder_name:
        builder = lookup_builder_by_name(builder_name, state)
    if builder:
        builder_risk, builder_factors = score_individual_builder(builder)

    # Property composite (60% weight)
    property_composite = round(
        age_score * 0.15 / 0.60 +
        pipe_score * 0.15 / 0.60 +
        heater_score * 0.10 / 0.60 +
        permit_score * 0.08 / 0.60 +
        claims_history_score * 0.07 / 0.60 +
        protection_score * 0.05 / 0.60,
        1
    )

    # ─── Environmental Context (40% of total) ───
    lat, lon = geocode_zip(zip_code)

    climate_data = fetch_climate_data(lat, lon)
    climate_score = score_climate(climate_data)

    wq_data = get_water_quality(state)
    wq_score = score_water_quality(wq_data)

    pressure_data = get_pressure_data(state)
    pressure_score = score_pressure(pressure_data)

    claims_data = get_claims_data(state)
    area_claims_score = score_claims(claims_data)

    reg_data = get_regulatory(state)
    reg_score = score_regulatory(reg_data)

    # Environmental composite (40% weight)
    env_composite = round(
        climate_score * 0.10 / 0.40 +
        wq_score * 0.08 / 0.40 +
        pressure_score * 0.08 / 0.40 +
        area_claims_score * 0.08 / 0.40 +
        reg_score * 0.06 / 0.40,
        1
    )

    # ─── Total Composite ───
    total_composite = round(
        # Property factors (60%)
        age_score * 0.15 +
        pipe_score * 0.15 +
        heater_score * 0.10 +
        permit_score * 0.08 +
        claims_history_score * 0.07 +
        protection_score * 0.05 +
        # Environmental context (40%)
        climate_score * 0.10 +
        wq_score * 0.08 +
        pressure_score * 0.08 +
        area_claims_score * 0.08 +
        reg_score * 0.06,
        1
    )

    # Risk level
    if total_composite <= 25:
        risk_level = "Low"
        risk_color = "#22c55e"
    elif total_composite <= 45:
        risk_level = "Moderate"
        risk_color = "#f59e0b"
    elif total_composite <= 65:
        risk_level = "High"
        risk_color = "#f97316"
    elif total_composite <= 80:
        risk_level = "Very High"
        risk_color = "#ef4444"
    else:
        risk_level = "Critical"
        risk_color = "#dc2626"

    # Confidence level based on data completeness
    data_points = sum([
        bool(year_built), bool(pipe_material and pipe_source == "provided"),
        bool(water_heater_age is not None), bool(total_permits > 0),
        bool(builder), bool(db_property)
    ])
    if data_points >= 5:
        confidence = "High"
    elif data_points >= 3:
        confidence = "Moderate"
    else:
        confidence = "Low (limited property data)"

    # Namara device prevention mapping for this property
    prevention_items = []
    if pipe_score > 40:
        prevention_items.append({
            "risk": "Aging pipe failure",
            "prevention": "Small leak detection catches failures early, auto shut-off prevents catastrophic damage",
            "estimated_savings_pct": 65
        })
    if heater_score > 35:
        prevention_items.append({
            "risk": "Water heater failure",
            "prevention": "Pressure monitoring detects tank pressure buildup, thermal expansion relief prevents burst",
            "estimated_savings_pct": 70
        })
    if climate_score > 40 and climate_data.get("freeze_days", 0) > 10:
        prevention_items.append({
            "risk": "Freeze damage",
            "prevention": "In-pipe temperature monitoring with alerts before pipe-freezing temps reached",
            "estimated_savings_pct": 80
        })
    if pressure_score > 40:
        prevention_items.append({
            "risk": "High water pressure damage",
            "prevention": "20-second pressure monitoring detects spikes, supply-side pressure relief prevents damage",
            "estimated_savings_pct": 60
        })
    if not has_prv:
        prevention_items.append({
            "risk": "No pressure regulation",
            "prevention": "Supply-side pressure relief and optimization compensates for missing PRV",
            "estimated_savings_pct": 50
        })

    return {
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "latitude": lat if lat else None,
        "longitude": lon if lon else None,
        "composite_score": total_composite,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "confidence": confidence,
        "scored_at": datetime.utcnow().isoformat(),
        "score_type": "property_level",
        "property_data": {
            "year_built": year_built,
            "pipe_material": pipe_material,
            "pipe_material_source": pipe_source,
            "sqft": sqft,
            "stories": stories,
            "bathrooms": bathrooms,
            "water_heater_age_years": water_heater_age,
            "water_heater_type": water_heater_type,
            "has_prv": has_prv,
            "has_expansion_tank": has_expansion_tank,
            "prior_water_claims": prior_claims,
            "prior_claim_total_cost": prior_claim_cost,
            "total_plumbing_permits": total_permits,
            "last_plumbing_permit_year": last_permit_year,
            "from_database": bool(db_property),
            "enrichment_source": enrichment_source,
            "enrichment_data": enrichment_data if enrichment_data else None,
            "data_sources": data_sources,
        },
        "property_factors": {
            "home_age": {"score": age_score},
            "pipe_material": {"score": pipe_score},
            "water_heater": {"score": heater_score},
            "permit_history": {"score": permit_score},
            "prior_claims": {"score": claims_history_score},
            "protection_devices": {"score": protection_score},
            "subtotal": property_composite,
        },
        "environmental_factors": {
            "climate": {"score": climate_score, "data": climate_data},
            "water_quality": {"score": wq_score, "data": wq_data},
            "pressure": {"score": pressure_score, "data": pressure_data},
            "area_claims": {"score": area_claims_score, "data": claims_data},
            "regulatory": {"score": reg_score, "data": reg_data},
            "subtotal": env_composite,
        },
        "layers": {
            "claims": {"score": area_claims_score, "data": claims_data},
            "climate": {"score": climate_score, "data": climate_data},
            "water_quality": {"score": wq_score, "data": wq_data},
            "infrastructure": {"score": round(age_score * 0.5 + pipe_score * 0.5, 1), "data": {
                "median_year_built": year_built or 1980,
                "pct_pre_1980": 75 if (year_built or 1980) < 1980 else 15,
                "pct_pre_1960": 60 if (year_built or 1980) < 1960 else 5,
            }},
            "pressure": {"score": pressure_score, "data": pressure_data},
            "builder_quality": {"score": builder_risk, "data": {}},
            "regulatory": {"score": reg_score, "data": reg_data},
        },
        "builder": {
            "name": builder.get("name") if builder else builder_name,
            "grade": builder.get("grade") if builder else None,
            "risk_score": builder_risk,
            "factors": builder_factors,
            "found_in_database": bool(builder),
        },
        "namara_prevention": prevention_items,
        "namara_gap": [
            "Real-time water pressure monitoring (20-sec intervals)",
            "Small and large leak detection with auto shut-off",
            "Freeze protection with in-pipe temperature monitoring",
            "Thermal expansion relief",
            "Supply-side pressure relief and optimization"
        ]
    }
