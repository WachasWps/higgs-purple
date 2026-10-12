import json,sys
B="/Users/wachas/Documents/higgs-purple/dub/feedback/script_audit/"
# per video: shots on_screen list; lines: id -> (on_screen_during, new or None, reason)
D={
"7ea55172":{
 "shots":["Woman frowning in bathroom mirror, green grease-blob villain on her cheek, talking sunscreen tube on the counter.",
  "Full-screen colour wheel 'Purple Tint Instant Glow for Indian skin tone': purple marker at top linked to yellow at bottom.",
  "DERMDOC Ultra Violet tube lying on a swirl of lavender cream.",
  "Woman smoothing lavender tint onto her cheek, 'PURPLE TINT' caption, grease villain on her shoulder.",
  "Before/after split of the woman (before top, after bottom); difference is subtle.",
  "Woman's face inside a blue hex SPF shield deflecting sun rays, 'SPF 50 PA+++' caption.",
  "Daytime city street: tube with shield and colour-wheel badge, woman smiling, green villains walking off."],
 "lines":{
  1:("Grease villain on cheek in mirror","Sticky shine, on duty!","Matches villain; trimmed to 1.93s slot"),
  2:("Mirror scene, villains on her face","And I brought dullness.","Villain visible; trimmed to 1.75s slot"),
  3:("Tube stands up to the villains",None,"Fits (3 words, 0.1 over budget, negligible)"),
  4:("Colour wheel, purple linked to yellow","Opposite yellow, purple cancels yellow-looking dullness.","Explain wheel fully (yellow-looking) within 6.9-word budget"),
  5:("Tube on lavender swirl, then woman applying purple tint","Purple tint for Indian skin.","Trim to budget; still matches tint being applied"),
  6:("End of tint application, then before/after split","Niacinamide helps: instant, even-looking glow.","B/A split on screen: talk result, keep niacinamide"),
  7:("Tail of B/A, then SPF 50 PA+++ shield deflecting rays",None,"Matches shield graphic"),
  8:("Daylight street, tube with shield, villains leaving","Glow on, shield up. Bye, villains!","Old line 7 words over budget; react to shield + departing villains"),
 }},
"89697c77":{
 "shots":["Night vanity: tired woman in orange pyjamas, purple Snooze villain tempting her, small jar on table.",
  "Caped talking jar on a night counter, pointing.",
  "Jar opens with glowing moon, 'OVERNIGHT BRIGHTENER' caption.",
  "Open jar with glowing orbs labelled '2% Kojic Acid' and 'Niacinamide & Alpha Arbutin'.",
  "Macro of a spoon lifting thick white cream from the jar.",
  "Woman at night dotting cream on forehead and cheek (spots visible).",
  "Woman at night with hands on her face, skin looks dewy and absorbed.",
  "Woman asleep, Snooze floating; then morning sunlight floods in.",
  "'AFTER' clip: woman in pyjamas in dim light, sad expression, spots still visible.",
  "Before/after split, but both halves show the same sad, spotty face in night lighting."],
 "lines":{
  1:("Snooze tempting tired woman at vanity",None,"Villain on screen"),
  2:("Jar on counter, pointing","Sleep, yes. Skipping, no.","Fits visually; trimmed to 1.75s slot"),
  3:("Jar with 'OVERNIGHT BRIGHTENER' and moon","Bedtime is brightening time.","Echoes caption; old 6 words in 1.79s"),
  4:("Three glowing actives over jar","Three actives, one 3XPERT formula.","Describe the orbs; fix spelling 3XPERT; fit 5-word budget"),
  5:("Spoon lifting rich cream",None,"Villain reacts to rich texture on screen"),
  6:("Woman dotting cream on face at night","Dot, smooth, massage.","Match dotting action; old line over budget"),
  7:("Dewy face, hands on cheeks, then asleep","Fully absorbed. Now, beauty sleep.","Trim to budget; still matches absorb then sleep"),
  8:("Morning light, then 'AFTER' clip (shot looks wrong: sad, spots)","Two weeks later? Clearer-looking skin!","Leads into result; hedged. Shot S9 contradicts it, needs replacing"),
  9:("Before/after split (both halves look like 'before')",None,"End tag; result carried by line 8. B/A shot needs a real 'after'"),
 }},
"906fbf3c":{
 "shots":["Night: worried woman touching spotty cheek, smoky dark-spot villain beside her.",
  "Talking jar pressing a glowing three-button panel on a night counter.",
  "Jar opens, '2% KOJIC ACID' caption, jar raising a finger.",
  "Jar of cream with three glowing orbs (the three actives) circling.",
  "Golden '2% Kojic Acid' hexagon blasting dark-spot villains.",
  "Macro of rich white cream peak in the jar.",
  "Fingertip scooping cream from the jar at night.",
  "Close-up cheek: dark-spot villain dissolving, skin clearing.",
  "Before/after split: both halves frowning; after has slightly fewer spots.",
  "Jar on night counter, end card '2% Kojic Acid Night Cream, Sleep to Glow'."],
 "lines":{
  1:("Dark-spot villain on her cheek at night",None,"Villain on screen"),
  2:("Jar at control panel, then '2% KOJIC ACID' caption","My shift now. Two percent Kojic Acid!","Match on-screen caption; old line over budget"),
  3:("Three glowing actives circling the jar","Three glowing actives, one 3XPERT formula.","Describe orbs; fix 3XPERT spelling; fit budget"),
  4:("Kojic hexagon blasting spot villains","Three?! Unfair!","Villain reaction kept; trimmed to 0.95s slot"),
  5:("End of blast, then rich cream macro","Rich, creamy, night-ready.","Describe the texture shown; old line far over budget"),
  6:("Fingertip scoop, then spot villain dissolving","Scoop, massage in, and let me work.","Match scoop + villain dissolving; fit budget"),
  7:("Before/after split (night lighting)","Two weeks: spots look reduced!","B/A must state 2-week result; removed morning wording over night shot"),
  8:("End card with product name",None,"Fits end card"),
 }},
"a5c00002":{
 "shots":["Woman in bed at night, half-asleep, eyes opening.",
  "She looks over at the jar on the lamp-lit nightstand.",
  "She reaches and picks up the jar.",
  "Close-up: she points at dark spots on her cheek.",
  "Before/after split: spots on top, clearer glowing cheek below.",
  "Filming herself, she dots cream on forehead and cheeks.",
  "She rubs the cream into her cheek.",
  "She puts the jar back on the lamp-lit nightstand.",
  "Lights off, she is asleep.",
  "End card: DERMDOC 2% Kojic Acid Night Cream, 'Available on Purplle', 'Shop Now' (no voice)."],
 "lines":{
  1:("Woman in bed at night, waking","Almost asleep, then I remembered,","Old line 11 words in 2.57s slot"),
  2:("She glances at the jar","Wait, my skincare!","Fit 1.47s slot"),
  3:("She picks up the jar","Never skipping this.","Fit 1.57s slot"),
  4:("Pointing at spots on cheek","See these stubborn spots?","React to spots shown; fit budget"),
  5:("Before/after split","Two weeks later, looking clearer!","B/A: two-week result, hedged; fit budget"),
  6:("Dotting cream on face","DERMDOC 2% Kojic Acid Night Cream,","Dropped 'So'; full product name kept, ~0.5 word over budget (unavoidable)"),
  7:("Rubbing cream in, then jar back by the lamp","Massage it in, lights off.","Match massage action; fit budget"),
  8:("Lights off, asleep","Sleep. Let it work.","Fit budget; matches sleeping shot"),
 }},
"a9be56d9":{
 "shots":["Macro of skin texture with dark spots.",
  "Woman at night touching spotty cheek in mirror.",
  "Hand placing the jar on a blue reflective surface.",
  "Fingertip scooping cream from the jar, lamp-lit night.",
  "Jar with three glowing orbs circling (the three actives).",
  "Skin cross-section: serum streams reaching dark pigment clusters.",
  "Woman applying cream dots to cheeks at night.",
  "Woman asleep, jar on nightstand, blue night light.",
  "Morning: woman smiling in bright bedroom, touching her cheek.",
  "Before/after split: spots on top, clearer skin below."],
 "lines":{
  1:("Skin macro and woman touching spots",None,"Fits"),
  2:("Hero jar, then scoop",None,"Brand intro over hero jar; product name, marginally over budget"),
  3:("Three glowing actives",None,"Names the three actives on screen"),
  4:("Skin science graphic, then night application","Targets the look of dark spots.","Fit budget; matches science graphic"),
  5:("Asleep at night, then morning wake",None,"Night then morning wording matches shots; at budget"),
  6:("Before/after split","After two weeks, clearer-looking skin.","B/A: state two-week result"),
 }},
"b4c787e1":{
 "shots":["Macro of skin texture with dark spots.",
  "Woman in daylight, spots visible, neutral expression.",
  "Hand placing the jar on a blue reflective surface.",
  "Open jar on a lamp-lit bedside table at night.",
  "Jar with three glowing orbs circling (the three actives).",
  "Skin cross-section: serum streams reaching dark pigment clusters.",
  "Woman applying cream dots to cheeks at night.",
  "Morning: woman smiling in bright bedroom.",
  "Before/after split: spots on top, clearer skin below."],
 "lines":{
  1:("Spot macro, woman with spots",None,"Fits"),
  2:("Hero jar, then jar at bedside night","Meet DERMDOC 2% Kojic Acid Night Cream.","Old dangling clause overran slot; standalone intro over jar"),
  3:("Three glowing actives","Three actives: Kojic Acid, Niacinamide, Alpha Arbutin.","Name the orbs as three actives"),
  4:("Science graphic, then night application","Targets the look of spots. Apply nightly.","Covers both shots; old line 11 words"),
  5:("Morning wake, then before/after split","Wake up glowing. After two weeks, spots look reduced.","Morning wording over morning shot; B/A result"),
 }},
"bd3b8af7":{
 "shots":["Night: woman, eyes closing, cuddling the smiling talking jar.",
  "Jar lid lifts, three cute ingredient heroes (gold, silver, pink) pop out of the cream.",
  "Golden Kojic Acid hero with magnifier scanning spots on her cheek.",
  "Silver Niacinamide hero glowing on cheek, brightening the area.",
  "Pink Alpha Arbutin droplet with magnifier on spotty cheek.",
  "Fingertip scooping cream from the jar at night.",
  "Before/after split: spots on top, clearer skin below.",
  "End shot: jar with the three heroes on a bright cream-swirl set."],
 "lines":{
  1:("Woman drifting off holding jar, then heroes pop out","You sleep. Team, clock in!","Fit 2.2s slot; still cues the team popping out"),
  2:("Heroes pop out, then Kojic hero scanning spots","Kojic Acid here, scanning the look of dark spots.","Match magnifier action; old line 14 words"),
  3:("Niacinamide hero glowing on cheek","Niacinamide! Brightening dull-looking skin.","Fit 2.0s slot"),
  4:("Alpha Arbutin hero on cheek","Even-looking tone, mine!","Fit 1.37s slot"),
  5:("Scoop, before/after split, end card","Rich cream. Two weeks, spots look reduced. DERMDOC 2% Kojic Acid Night Cream.","Add B/A result over split; keep name for end card"),
 }},
"c01adcce":{
 "shots":["Macro of skin with sun rays across it.",
  "DERMDOC Ultra Violet tube on a bright vanity with a lavender swatch.",
  "Tube on a lavender cream swirl.",
  "Lavender hex shield deflecting sun rays.",
  "Woman in daylight, skin looks dull (before).",
  "Full-screen colour wheel 'Purple Tint Instant Glow for Indian skin tone', purple linked to yellow.",
  "Macro of a drop blending into skin and vanishing.",
  "Woman smiling with glowing skin.",
  "Before/after split, subtle glow difference.",
  "Woman smiling outdoors in daylight city."],
 "lines":{
  1:("Sun rays on skin, then tube","The sun shows. Protection shouldn't.","Old 8 words in 2.45s; keeps invisible-protection idea"),
  2:("Tube on swirl, then shield deflecting rays",None,"Fits"),
  3:("Dull woman, then colour wheel","Purple sits opposite yellow, cancelling yellow-looking dullness.","Explain wheel properly; fit budget"),
  4:("Cream blending away, then glowing woman",None,"Fits"),
  5:("Before/after split, then outdoor glow",None,"Instant glow result matches"),
 }},
"c51221b6":{
 "shots":["White Cast villain rolling ashy streaks on worried woman's cheek.",
  "Smiling woman with DERMDOC tube, White Cast villain shocked beside it.",
  "Purple Tint droplet pushes the White Cast villain off her cheek.",
  "Full-screen colour wheel 'Purple Tint Instant Glow for Indian skin tone', purple linked to yellow.",
  "SPF 50 PA+++ shield hero blocking angry UV fireballs, '4% Niacinamide' ring.",
  "Silver Niacinamide hero clearing grey dullness haze from her cheek.",
  "Macro of a drop blending into skin and vanishing.",
  "Tube with Purple Tint, Shield and Niacinamide heroes; White Cast villain flees (no line)."],
 "lines":{
  1:("Villain rolling white streak",None,"Villain on screen"),
  2:("Villain rolling white streak","Everyone sees your sunscreen!","Fit 1.8s slot"),
  3:("Tube with shocked villain",None,"Fits"),
  4:("Purple droplet pushes villain off, then colour wheel","Shoo! Opposite yellow, I cancel yellow-looking dullness.","React to push-off, then explain wheel"),
  5:("Shield blocking UV fireballs",None,"Fits"),
  6:("Niacinamide hero clearing grey haze",None,"Fits"),
  7:("Drop blending into skin","Blends in. Just instant glow.","Describe vanishing blend; fit budget"),
 }},
"caf29456":{
 "shots":["Annoyed woman on sunny balcony touching her cheek.",
  "Full-screen colour wheel 'Purple Tint Instant Glow for Indian skin tone', purple linked to yellow.",
  "Lavender cream swirl next to tube, fingertip touching it.",
  "Lavender stripe swatched on the back of a hand.",
  "Swatch rubbed in, turning clear on the hand.",
  "Woman on balcony dotting lavender cream on her face and spreading it.",
  "Before/after split, subtle glow difference.",
  "Woman holding tube in sunshine inside a protective bubble."],
 "lines":{
  1:("Annoyed woman on balcony","Why's my skin so dull?","Fit 2.47s slot"),
  2:("Colour wheel","Purple sits opposite yellow.","Fit 1.8s slot; wheel visible"),
  3:("Colour wheel","It cancels yellow-looking dullness.","Fit budget"),
  4:("Lavender cream swirl, finger touching","Purple? Won't stay.","Fit 1.35s slot"),
  5:("Swatch blending clear on hand","Blends clear. No white cast.","Match blend; fit budget"),
  6:("Dotting and spreading on face, then B/A split","Dot it, blend it. With 4% Niacinamide: Instant Glow, even-looking skin.","Match application then result; old 18 words"),
  7:("Holding tube in sun, protective bubble",None,"Fits"),
 }},
}
out=[]
for vid,d in D.items():
    m=json.load(open(B+vid+"/manifest.json"))
    L=m["lines"]
    shots=[{"n":s["n"],"start":s["start"],"end":s["end"],"on_screen":d["shots"][i]} for i,s in enumerate(m["shots"])]
    assert len(d["shots"])==len(m["shots"]),vid
    lines=[]
    for i,l in enumerate(L):
        slot = (L[i+1]["start"]-l["start"]-0.15) if i+1<len(L) else (l["end"]-l["start"]+0.5)
        osd,new,reason=d["lines"][l["id"]]
        keep = new is None
        txt = l["en"] if keep else new
        w=len(txt.split())
        lines.append({"id":l["id"],"start":l["start"],"slot_s":round(slot,2),"speaker":l["speaker"],"current":l["en"],
          "on_screen_during":osd,"verdict":"keep" if keep else "rewrite","new":txt,"words":w,"reason":reason})
        flag = "OVER" if w>2.4*slot+1e-9 else ""
        out.append(f"{vid} L{l['id']} {'K' if keep else 'R'} {w}/{2.4*slot:.1f} {flag} {txt}")
    json.dump({"video":vid,"shots":shots,"lines":lines},open(B+vid+"/proposal.json","w"),indent=1,ensure_ascii=False)
print("\n".join(out))
