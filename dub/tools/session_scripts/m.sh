FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg; cd /Users/wachas/Documents/higgs-purple/dub/tools/audit_s6/fr
m(){ out=$1; shift; args=(); fc=""; i=0; for f in "$@"; do args+=(-i "$f"); fc="$fc[$i]scale=540:-1[v$i];"; i=$((i+1)); done; for j in $(seq 0 $((i-1))); do fc="$fc[v$j]"; done; fc="${fc}hstack=$i"; $FF -v error -y "${args[@]}" -filter_complex "$fc" ../M_$out.jpg; }
m a1 can-we*_8.6.png can-we*_9.0.png can-we*_16.5.png can-we*_17.0.png
m a2 can-we*_17.2.png can-we*_17.4.png can-we*_23.0.png can-we*_25.5.png
m b1 finding*_8.5.png finding*_13.0.png finding*_18.5.png finding*_18.8.png
m b2 finding*_19.0.png finding*_25.0.png finding*_26.6.png finding*_27.5.png
m c1 it-act*_1.5.png it-act*_3.0.png it-act*_12.4.png it-act*_12.9.png
m c2 it-act*_15.5.png it-act*_19.5.png it-act*_22.0.png it-act*_24.5.png
m d1 it-is*_6.5.png it-is*_9.0.png it-is*_17.3.png it-is*_17.9.png
m d2 it-is*_22.0.png it-is*_24.0.png it-is*_26.5.png it-is*_32.5.png
m e1 will*_1.0.png will*_5.0.png will*_12.0.png will*_15.5.png
m e2 will*_15.9.png will*_21.5.png will*_25.0.png will*_27.5.png
