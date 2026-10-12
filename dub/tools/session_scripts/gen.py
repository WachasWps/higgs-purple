import json
B='/Users/wachas/Documents/higgs-purple/dub/feedback/script_audit/'
# per video: shots on_screen list; lines dict id -> (on_screen_during, new or None, reason)
D={
'00b304b4':{
'shots':["Woman in beige blazer at vanity mirror in the morning; DERMDOC Ultra Violet box and tube on the desk.",
"Angry sun villain at the window with White Cast, Greasiness and Dullness cloud firing rays.",
"Talking DERMDOC Ultra Violet tube held up, with SPF shield, purple droplet and niacinamide molecule team in purple swirl.",
"SPF 50 PA+++ shield on her cheek blocking golden UV rays with a bubble.",
"Full-screen colour wheel, 'Purple Tint Instant Glow for Indian Skin Tone', marker linking purple top to yellow bottom.",
"Close-up cheek: gold Greasiness blob and grey Dullness cloud; purple droplet flies in and the cloud fades (niacinamide character not visible).",
"Macro of a sunscreen drop on brown skin shrinking as it blends in under sunlight.",
"Woman outdoors in daylight city, smiling with the tube and hero team in front, villains defeated behind."],
'lines':{
1:("Woman at vanity getting ready, tube on desk.",None,"Fits the morning setup."),
2:("Sun villain gang at the window.",None,"Villain on screen, fits."),
3:("Talking tube with its hero team.",None,"Fits the team line-up."),
4:("SPF shield blocking UV rays on her cheek.",None,"Fits."),
5:("Colour wheel, purple opposite yellow.","Purple cancels yellow!","Must explain the wheel; 1.4 s slot only fits 3 words, so state purple-vs-yellow directly."),
6:("Greasiness blob and Dullness cloud on cheek being cleared.","I'll brighten that dullness!","Instant-glow claim didn't match; dullness cloud is what's visible."),
7:("Sunscreen drop blending into skin.","Fully blended. No residue.","Blend clip on screen; talk texture, not 'protection complete'."),
8:("Woman outdoors in daylight with tube and team.","Glowing. Let's go!","Matches but 6 words was ~1.7x over the 1.44 s slot; tightened."),
}},
'02bad3b3':{
'shots':["Woman in pink pyjamas at night, touching dark spots on her cheek, holding the night cream jar.",
"From behind, she switches on the lamp and reaches for the jar on her vanity at night.",
"Night cream jar with three glowing orbs (the three actives) on a blue backdrop.",
"Fingertip scooping thick white cream from the jar.",
"At the mirror she dots cream on forehead, nose and cheeks.",
"Close-up: she massages the cream into her cheek, cream vanishing.",
"She sleeps in bed at night, jar on the nightstand.",
"Before/after split: dark spots on top, clearer-looking skin below (model differs from the creator).",
"Morning daylight: she smiles at the vanity, jar in front."],
'lines':{
1:("Night, touching dark spots, holding jar.","My dark spots looked so uneven.","Fits, but 10 words in a 2.6 s slot; tightened."),
2:("Reaching for the jar at the night vanity.","So, DERMDOC 2% Kojic Acid Night Cream.","Fits, but 12 words too long; tightened to product name."),
3:("Jar with three glowing active orbs.",None,"Matches the three-orb graphic; slightly long but acceptable."),
4:("Fingertip scooping cream.","Thick, rich texture.","Matches; cut from 6 to 3 words for 1.35 s slot."),
5:("Dotting cream on face, then massaging it in.","Dot it on, massage till it absorbs.","Matches; 15 words was double the slot."),
6:("She sleeps at night.","Then it works overnight.","Matches; 9 words was too long for 1.9 s."),
7:("Before/after split.","After two weeks, spots look reduced.","Matches; 14 words cut to fit 2.55 s."),
8:("Morning, smiling with the jar.",None,"Morning wording over morning shot; fits."),
}},
'23850d94':{
'shots':["Woman with spots at night holding the bespectacled professor jar with a pointer.",
"Professor jar in a mini classroom with chalkboard and three ingredient characters (gold, silver, pink).",
"Gold Kojic Acid hero beside a dark-spot villain on her cheek; caption '2% Kojic Acid targets dark spots'.",
"Silver Niacinamide hero sweeping a grey dullness cloud; caption 'Niacinamide brightens dull-looking skin'.",
"Pink Alpha Arbutin droplet fading a brown spot; caption is garbled ('Heip:evoen''s Hpoke skin tone').",
"Fingertip scooping rich white cream from the jar in a warm bedroom.",
"Before/after split: freckled dark spots on top, clearer-looking skin below.",
"End card: DERMDOC Honest Science, professor jar with gold and pink characters, '3 Ingredients. 1 Night Cream'."],
'lines':{
1:("Woman at night holding the professor jar.",None,"Fits."),
2:("Classroom with three ingredient characters.",None,"Fits."),
3:("Kojic hero vs dark spot, caption on screen.",None,"Fits caption."),
4:("Niacinamide sweeping dullness, then Alpha Arbutin fading a spot.","Two: brighter-looking. Three: even-looking tone.","Matches visuals; hedged 'brighter skin' and trimmed."),
5:("Fingertip scooping cream from the jar.","Rich cream. Apply tonight; it absorbs.","Scoop on screen; talk texture/absorbing, keep night."),
6:("Before/after split, then the end card.","After two weeks, spots look reduced. Class dismissed.","Before/after on screen needs result line; brand is on the end card."),
}},
'291827ba':{
'shots':["Worried woman as sun villain, White Cast and Dullness attack her cheek.",
"DERMDOC Ultra Violet tube on a bathroom counter with small blue cube and yellow star characters; a hand reaches in (no courtroom/judge look).",
"Courtroom: SPF shield lawyer beside a glass dome trapping sun villains, tube on the bench; 'SPF 50 PA+++'.",
"White Cast villain smearing chalky powder on her cheek.",
"Full-screen colour wheel, 'Purple Tint Instant Glow for Indian Skin Tone', purple top linked to yellow bottom.",
"Purple droplet pushing away the grey dullness cloud on cheek; caption '4% NIACINAMIDE'.",
"Macro of a sunscreen drop blending into brown skin under sunlight.",
"Tube with hero team on counter; villains locked in a glass box."],
'lines':{
1:("Villains attacking her cheek.",None,"Villain on screen; fits."),
2:("Tube on the counter with small characters.",None,"Line fine; the shot doesn't look like a courtroom (flagged)."),
3:("SPF shield and dome trapping sun villains.",None,"Fits."),
4:("White Cast smearing powder, then the colour wheel.","Two: purple, opposite yellow, cancels dullness.","Wheel needs the 'opposite yellow' explanation."),
5:("Droplet clearing dullness, '4% NIACINAMIDE'.",None,"Fits."),
6:("Sunscreen drop blending in.","Verdict: blends fully, no white cast.","Blend clip on screen; talk texture."),
7:("Team with villains locked away.",None,"Fits."),
}},
'33c29291':{
'shots':["White Cast villain smearing grey-white on her cheek; talking tube fights it with a purple sponge.",
"Talking tube points at a colour wheel with arrow purple-to-yellow and skin-tone swatches; White Cast looks sad.",
"Lavender cream swatch rubbed on a hand in sunlight until it vanishes.",
"Woman spreading lavender cream on her cheek.",
"Before/after split, same woman, brighter-looking skin below.",
"Woman in sunlight; a shield deflects UVA and UVB.",
"Smiling woman; colour wheel and swatches beside her, confused White Cast with '??'."],
'lines':{
1:("White Cast smearing her cheek.",None,"Villain on screen; fits."),
2:("Tube fighting White Cast.",None,"Fits."),
3:("Tube pointing to the colour wheel.",None,"Explains the wheel; fits."),
4:("Lavender cream blending into hand.","Blends fully into Indian skin tones.","Swatch on screen; talk blending."),
5:("Cheek application, then before/after split.","4% Niacinamide: instant, radiant-looking glow.","Before/after needs the result."),
6:("UVA/UVB shield in sunlight.",None,"Fits."),
7:("Smiling woman, confused White Cast.",None,"Fits."),
}},
'390113f1':{
'shots':["Woman asleep at night; dark-spot and dullness villains stamping on her cheek.",
"Night cream jar on nightstand wakes up; gold, silver and pink actives burst out.",
"On her cheek, Kojic Acid hero hits dark spots ('2% Kojic Acid targets dark spots'), then Niacinamide clears dullness.",
"Jar with three glowing active orbs on blue backdrop.",
"Before/after split: spots on top, clearer-looking skin below.",
"End card: sleepy jar with three actives, 'Target Dark Spots While You Sleep'."],
'lines':{
1:("Villains on sleeping woman's cheek.",None,"Villain on screen; fits."),
2:("Jar waking, actives bursting out.","My team's awake!","'So is my night team' contradicts the team visibly springing out."),
3:("Team leaves jar, then Kojic and Niacinamide fight spots and dullness.","Shh, we're working. I'm on spots, Niacinamide's on dullness.","Shot 3 was silent; line extended within its 6.1 s slot to cover the visible action."),
4:("Three-orb jar, then before/after split.","Three actives. Two weeks: spots look reduced.","Orbs then before/after; cover both."),
5:("End card 'Target Dark Spots While You Sleep'.",None,"Fits."),
}},
'3d01d9fc':{
'shots':["Creator with curly hair in coral top talking by a sunny window.",
"Full-screen colour wheel, purple top linked to glowing yellow bottom.",
"Tube with lavender cream swirl; fingertip touches it.",
"Lavender swatch rubbed on hand in sunlight until it vanishes.",
"She dots lavender cream on face and blends it in.",
"Cheek close-up with glowing niacinamide molecule graphic.",
"Before/after split, same creator.",
"She sits at an outdoor cafe holding the tube under a sun-shield bubble."],
'lines':{
1:("Creator talking by window.","My dull skin? Sunscreen didn't help.","Fits but 11 words too long."),
2:("Colour wheel.","Purple sits opposite yellow, cancelling yellow-looking dullness.","Explains wheel; trimmed from 12 words."),
3:("Texture macro with finger.","Blend test time.","Fits; trimmed for 1.45 s."),
4:("Hand swatch blending.","No residue, no white cast.","Fits; trimmed."),
5:("Dotting and blending on face.","Blends right into Indian skin tones.","Application on screen; talk blending."),
6:("Niacinamide molecule on cheek, then before/after.","Plus, 4% Niacinamide: instant, even-looking glow.","Fits; trimmed, covers before/after."),
7:("End of before/after, then cafe with shield bubble.",None,"Fits shield shot."),
}},
'4010f985':{
'shots':["Macro of skin texture with light streaks.",
"Woman in white top, neutral expression, by a window.",
"Full-screen colour wheel, purple top linked to glowing yellow bottom.",
"Tube on a lavender cream swirl.",
"Close-up of tube's holographic ULTRA VIOLET lettering.",
"Lavender cream ribbon folding (texture).",
"Woman with lavender dots on her face, starting to blend.",
"Sunscreen drop blending into skin.",
"Woman smiling, glowing-looking skin.",
"Before/after split.",
"Woman on a balcony holding the tube in daylight."],
'lines':{
1:("Skin macro, then woman's neutral face.",None,"Fits."),
2:("Colour wheel.",None,"Explains wheel; fits."),
3:("Tube, holo label, texture.",None,"Fits."),
4:("Dots on face, blend drop, smiling.",None,"Fits."),
5:("Before/after split.","Instant glow, made for Indian skin.","Before/after needs result."),
}},
'426b77bb':{
'shots':["White cream ribbon twisting on dark blue.",
"Woman at night mirror touching dark spots.",
"Hand opening the night cream jar.",
"Open jar on a bedside table at night.",
"Jar with three glowing active orbs.",
"Woman at night massaging cream into her cheeks.",
"She sleeps, jar on nightstand.",
"Morning: she wakes and smiles in daylight.",
"Before/after split."],
'lines':{
1:("Cream ribbon, then woman touching dark spots.","Dark spots? Try three actives together.","Old line didn't react to dark spots on screen."),
2:("Jar opened, jar on nightstand.",None,"Fits."),
3:("Three-orb jar.",None,"Fits."),
4:("Applying at night, then sleeping.",None,"Fits."),
5:("Morning wake-up in daylight.",None,"Morning over morning shot; fits."),
6:("Before/after split.","Two weeks: spots look reduced.","Before/after needs result."),
}},
'46d965c9':{
'shots':["Woman at night desk with glasses and hand mirror, checking her skin.",
"She picks up the jar and walks away from her night desk.",
"Jar on a bathroom counter, moon in the window.",
"Spatula scooping thick white cream.",
"At the mirror she dots cream on her face.",
"She massages cream into her face.",
"Jar with three glowing orbs.",
"Jar with three orbs swirling.",
"She sleeps, jar on the nightstand.",
"Before/after split (different model from the creator)."],
'lines':{
1:("Checking skin at night desk.","End of day: tired, uneven-looking skin.","Fits but 13 words was double the slot."),
2:("Picks up the jar.","Night reset starts here.","Fits; trimmed."),
3:("Jar on bathroom counter.",None,"Fits."),
4:("Spatula scoop.","Rich, thick, non-watery texture.","Fits; trimmed."),
5:("Dotting cream at the mirror.","Dot it on.","Fits; trimmed."),
6:("Massaging it in.","Massaged in, it absorbs fully.","Massaging on screen, not orbs."),
7:("Three-orb jar, then sleeping.","Glow Fusion Formula: Kojic Acid, Niacinamide, Alpha Arbutin, overnight.","Orbs on screen; name the actives."),
8:("Before/after split.","After two weeks, spots look reduced.","Fits; trimmed."),
}},
}
for v,d in D.items():
  m=json.load(open(B+v+'/manifest.json'))
  shots=[{"n":s['n'],"start":s['start'],"end":s['end'],"on_screen":d['shots'][i]} for i,s in enumerate(m['shots'])]
  assert len(d['shots'])==len(m['shots']),v
  L=m['lines'];out=[]
  for i,l in enumerate(L):
    slot=round((L[i+1]['start']-l['start']-0.15) if i+1<len(L) else (l['end']-l['start']+0.5),2)
    osd,new,reason=d['lines'][l['id']]
    verdict='keep' if new is None else 'rewrite'
    txt=l['en'] if new is None else new
    w=len(txt.split())
    out.append({"id":l['id'],"start":l['start'],"slot_s":slot,"speaker":l['speaker'],"current":l['en'],"on_screen_during":osd,"verdict":verdict,"new":txt,"words":w,"reason":reason})
    flag='OVER' if w>slot*2.4 else ''
    if flag and verdict=='keep': out[-1]['reason']+=' Kept although %d words exceeds the %.1f-word budget (pre-existing timing).'%(w,slot*2.4)
    print(v,l['id'],verdict,w,round(slot*2.4,1),flag,txt)
  json.dump({"video":v,"shots":shots,"lines":out},open(B+v+'/proposal.json','w'),indent=1,ensure_ascii=False)
