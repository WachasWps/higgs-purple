FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg; O=/Users/wachas/Documents/higgs-purple/dub/tools/audit_s6; D=/Users/wachas/Documents/higgs-purple/dub/Final_Deliverables/3_UGC_Ads/Purple_Sunscreen_PS/Bengali_WB
args=(); fc=""; i=0
for spec in it-actually-blends-in:12.9 it-actually-blends-in:19.5 will-it-turn-me-purple:27.5 will-it-turn-me-purple:19.0 can-we-talk-about-annoying-sunscreens:21.0 finding-a-good-sunscreen:23.0 it-is-literally-purple:22.0 can-we-talk-about-annoying-sunscreens:31.9 it-actually-blends-in:3.0 will-it-turn-me-purple:5.0; do n=${spec%%:*}; t=${spec##*:}
args+=(-ss $t -i "$D/PS_UGC_ugc-${n}_Bengali.mp4"); fc="$fc[$i]crop=360:240:720:1680,drawtext=text='$i':fontsize=30:fontcolor=red:x=5:y=5[v$i];"; i=$((i+1)); done
for j in $(seq 0 $((i-1))); do fc="$fc[v$j]"; done
$FF -v error -y "${args[@]}" -filter_complex "${fc}xstack=inputs=$i:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|w0+w1+w2+w3_0|0_h0|w0_h0|w0+w1_h0|w0+w1+w2_h0|w0+w1+w2+w3_h0" -frames:v 1 $O/WM.jpg
