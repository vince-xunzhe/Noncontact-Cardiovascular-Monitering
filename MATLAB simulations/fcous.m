function [x,y,r,ratio]=fcous(img)
bound=200;
[hor,ver]=size(img);
seg=zeros(hor,ver);
threshold=0.5*max(img(:));
count=0;
num=0;
for i=1:hor
    for j=1:ver
        if img(i,j)>threshold
            seg(i,j)=img(i,j);
            num=num+img(i,j);
            count=count+1;
        else
            seg(i,j)=0;
        end
    end
end
I_max=max(seg(:))
I_av=num/count
ratio=I_av/I_max

[x_0,y_0]=find(seg>threshold);
x0=ceil(mean(x_0));%圆心横坐标
y0=ceil(mean(y_0));%圆心纵坐标

%计算统计中心和区域 ROI
h=(x0-bound+1):(x0+bound);
w=(y0-bound+1):(y0+bound);

data1=seg(h,w);
[m,n]=size(data1);
I=sum(data1(:));
s_xc=sum((1:m)*data1);
s_yc=sum((1:n)*data1');
xc_in=s_xc/I;
yc_in=s_yc/I; % xc_in,yc_in是指在ROI的相对位置

I_av=1;
r=10;
while(1)
    r=r+3;
    b_x=(xc_in-r):(xc_in+r);
    b_y=(yc_in-r):(yc_in+r);
    I_av=sum(sum(data1(ceil(b_x),ceil(b_y))));
    if (I_av/I>0.8)
        break
    end
end

x=ceil(x0-bound+xc_in);
y=ceil(y0-bound+yc_in);
r=ceil(r/2+10);
end


