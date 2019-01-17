[p,s,mu] = polyfit((1:numel(C)),C,6);
f_y = polyval(p,(1:numel(C))',[],mu);
C = C - f_y'; 

L=length(C);
Fs=45;
NFFT=2^nextpow2(L);
Y=fft(C,NFFT)/L;
f=Fs/2*linspace(0,1,NFFT/2+1);
figure,plot(f,2*abs(Y(1:NFFT/2+1)))
xlabel('Frequency (Hz)');
ylabel('Amplitude of spectrum');



%% detect all the peaks
figure,subplot(411),plot(C);hold on;grid on;
xlabel('Frames');ylabel('phaseCorrelation');title('Original waveform with peak detection');
[pks_ALL,locs_ALL]=findpeaks(C,'MinPeakDistance',1);
length_1=length(pks_ALL);
for o=1:length_1
    plot(locs_ALL(o), pks_ALL(o), 'r*', 'MarkerSize', 5); 
end
hold off;

%% detect the SBP peaks 
subplot(412),plot(C);hold on;grid on;
xlabel('Frames');ylabel('phaseCorrelation');title('Systolic peak detection');
[pks_SBP,locs_SBP]=findpeaks(C,'MinPeakDistance',30);
length_SBP=length(pks_SBP);
gaps=[];
for o=1:length_SBP
    plot(locs_SBP(o), pks_SBP(o), 'r*', 'MarkerSize', 5); 
    if (o<(length_SBP-1))
        gaps=[gaps,locs_SBP(o+1)-locs_SBP(o)];
    end
end
hold off;


%% detect the AUG peaks
locs_AUG=[];
pks_AUG=[];
subplot(413),plot(C);hold on;grid on;
xlabel('Frames');ylabel('phaseCorrelation');title('Second systolic peak detection');
for i=1:length_SBP
    for j=1:length_1
        if (locs_SBP(i) == locs_ALL(j))
            locs_AUG=[locs_AUG,locs_ALL(j+1)];
            pks_AUG =[pks_AUG,pks_ALL(j+1)];
        end
    end
end
length_AUG=length(pks_AUG);
for o=1:length_AUG
    plot(locs_AUG(o), pks_AUG(o), 'r*', 'MarkerSize', 5); 
end

%% detection the Bottom 
m_gap=ceil(0.3*mean(gaps)/2);
locs_Bottom=[];
pks_Bottom=[];
for i=1:length_SBP
    if (locs_SBP(i)-m_gap<0) 
        vect=C(1:(locs_SBP(i)));
    else
        vect=C((locs_SBP(i)-m_gap):(locs_SBP(i)));
    end
    [ver hor]=min(vect);
    pks_Bottom=[pks_Bottom,ver];
    locs_Bottom=[locs_Bottom,locs_SBP(i)-m_gap+hor];
end
subplot(414),plot(C);hold on;grid on;
xlabel('Frames');ylabel('phaseCorrelation');title('Peak bottom detection');
length_Bottom=length(pks_Bottom);
for o=1:length_Bottom
    plot(locs_Bottom(o), pks_Bottom(o), 'r*', 'MarkerSize', 5); 
end
hold off;


%% Experiment, display in the same plot
figure,plot(C);hold on;grid on;
xlabel('Frames');
ylabel('phaseCorrelation');


for o=1:length_AUG
    plot(locs_AUG(o), pks_AUG(o), 'g*', 'MarkerSize', 5); 
end
for o=1:length_SBP
    plot(locs_SBP(o), pks_SBP(o), 'r*', 'MarkerSize', 5); 
end
for o=1:length_Bottom
    plot(locs_Bottom(o), pks_Bottom(o), 'k*', 'MarkerSize', 5); 
end


Pulse_Rate=ceil(length_SBP/((length(video)-begin_frame)/Rate)*60)*0.65

Augmentation=(pks_AUG./pks_SBP)  %%(pks_SBP-pks_AUG)./(pks_SBP-pks_Bottom)
Aug=[];
for i=1:(length(Augmentation)-2)
   a=mean([Augmentation(i),Augmentation(i+1),Augmentation(i+2)]);
   Aug=[Aug,a];
end

Augmentation_Index=mean(Aug)
