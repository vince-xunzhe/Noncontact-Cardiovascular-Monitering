clc;
clear;

mov=VideoReader('C:\Users\Administrator\Desktop\1.mp4');
nFrames=mov.NumberOfFrames;  %得到帧数 1809
H=mov.Height;  %得到高度
W=mov.Width;  %得到宽度
Rate=mov.FrameRate; %得到帧率 60

%等待三秒，重新分配视频结构,原视频，频域图
begin_frame=ceil(1*Rate);
P=im2double(rgb2gray(read(mov,begin_frame)));
[x_p,y_p,r,ratio]=fcous(P);
H=(x_p-r+1):(x_p+r);
W=(y_p-r+1):(y_p+r);

width=2*r;
height=2*r;

figure,imshow(P);
figure, imshow(P);
hold on;


plot([y_p-r+1 y_p+r],[x_p-r+1,x_p-r+1],'g')
plot([y_p+r y_p+r],[x_p-r+1 x_p+r],'g')
plot([y_p-r+1 y_p+r],[x_p+r x_p+r],'g')
plot([y_p-r+1 y_p-r+1],[x_p+r x_p-r+1],'g')


%video(1:(nFrames-begin_frame))=struct('movie',zeros(2*r,2*r),'filtered',zeros(2*r,2*r));
video(1:(nFrames-begin_frame))=struct('movie',zeros(2*r,2*r)); %1809-60
C=[];
time=0;
interation=0;
[m,n]=size(video);        %1750

%包含原图和滤波序列
for i=begin_frame:nFrames
    P=im2double(rgb2gray(read(mov,i)));
    Plate=P(H,W);
    video(i-begin_frame+1).movie=Plate;
%     d=avg_filter(Plate,5);
%     video(i-begin_frame+1).filtered=d;
    time = time+1
end

%图像归一化相关，找correlation peak location
C=[];
Cc=[];


for i=1:n
    if (i>1)
        image1 = video(i).movie;
        image2 = video(i-1).movie;
        Image1 = image1;
        Image2 = image2;
        FFT1 = fft2(double(Image1));
        FFT2 = conj(fft2(double(Image2)));
        FFTR = FFT1.*FFT2;
        FFTRN = (FFTR/abs((FFT1.*FFT2)));
        result = uint8(ifft2(double(FFTRN)));
        [delta_y,delta_x] = find(result==max(result(:)));
        Cc = [Cc;delta_y,delta_x];
        interation = interation+1
       
%        c=corr2(video(i).movie,video(i-1).movie);
%        [ypeak,xpeak]=find(c==max(c(:)));
%        C=[C;ypeak,xpeak];
       %C=[C,c];
    end
end

% for i=1:n
%     if (i>1)
%         c = corr2(video(i).movie,video(i-1).movie); %滤波器使用 coor2 normxcorr
% %       [ypeak,xpeak] = find(c==max(c(:)));
%         C = [C,c];
%         interation = interation+1
%     end
% end


a=length(Cc);
shift=[];
for j=1:a-1
    %s=sum(abs(C(j+1,:)-C(j,:)));
    s=sqrt(sum((Cc(j+1,:)-Cc(j,:)).^2));
    shift=[shift,s];
end

C=shift;

scale_frames=begin_frame:Rate:fix(nFrames);
scale_second=(scale_frames/Rate);
b=length(C);
figure,subplot(211),plot(C(20:b));
xlabel('Frame');
ylabel('Normalized phaseCorrelation');
%set(gca,'xtick',scale_frames);
%set(gca,'xticklabel',scale_second);

Fs=60;
fc=20;
wn=(2/Fs)*fc;
b=fir1(20,wn,'low',kaiser(21,3));
y=filter(b,1,C);
b=length(y);
subplot(212),plot(y(20:b));
xlabel('Frame');
ylabel('Normalized phaseCorrelation');
%set(gca,'xtick',scale_frames);
%set(gca,'xticklabel',scale_second);
