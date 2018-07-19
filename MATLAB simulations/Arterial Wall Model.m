clc;
clear;

E_1= 10;
E_2= 1;
E_3= 15;
n  = 0.005;
C  = 1;
theta=1;

q=E_1*E_2+E_1*E_3+E_2*E_3;
p=n*E_1*(1+E_3);
tau=0.005;
t1=0:0.0001:tau; 
t2=tau:0.0001:0.05;

response_before= (theta*(E_1+E_2)/tau)*( t1/q - (p/(q^2)) * exp(-(q/p)*t1) -  p/(q^2)) - (theta*n*E_1/(tau*q))*exp(-(q/p)*t1) + (theta*n*E_1/(tau*q));

response_after_1= (theta*(E_1+E_2)/tau)*( t2/q - (p/(q^2)) * exp(-(q/p)*t2) -  p/(q^2)) - (theta*n*E_1/(tau*q))*exp(-(q/p)*t2) + (theta*n*E_1/(tau*q));
response_after_2= -(theta*(E_1+E_2)/tau)*(t2-tau)/q - (theta*(E_1+E_2)/tau)*(1-exp(-(q/p)*(t2-tau)))/((q/p)^2) - (theta*n*E_1/(tau*q))*(1-exp(-(q/p)*(t2-tau)));
response_after_3=theta*( (E_1+E_2)*(1-exp(-(q/p)*(t2-tau)))/q + exp(-(q/p)*(t2-tau))/(1+E_3));

res_after=response_after_1+response_after_2+response_after_3;
x=tau*10500;
C=max(res_after);

figure,subplot(211),plot([0,x],[0,1],'LineWidth',2.5);hold on;
plot([x,550-x],[1,1],'LineWidth',2.5);
axis([0 600 0 1.5]);
t=0:0:0;
set(gca,'xtick',t); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',t); 
ylabel('Strain ¦Ò','FontSize',12,'FontWeight','bold');

subplot(212),plot([response_before,res_after],'LineWidth',2.5); hold on;
axis([0 600 -0.1 0.1]);
t=0:0:0;
set(gca,'xtick',t); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',t); 
ylabel('Stress ¦Å','FontSize',12,'FontWeight','bold');

E_1= 100;
E_2= 10;
E_3= 150;
n  = 0.01;
C  = 1;
ta=0.05;

p=n*E_1*(1+E_3);
q=E_1*E_2+E_1*E_3+E_2*E_3;
ta=0.05

t1=0:0.0001:ta;
t2=ta:0.0001:0.1;

response1=(E_1+E_2)/p*(1-exp(-1*t1*q/p))+(1*exp(-1*t1*q/p)/(1+E_3));
C=(E_1+E_2)/p*(1-exp(-1*ta*q/p))+(1*exp(-1*ta*q/p)/(1+E_3));
response2=C*exp(-1*(t2-ta)*q/p);
response=[response1,response2];

[a1,b1]=size(response1);
[a2,b2]=size(response2);
[a, b ]=size(response);

x=10000*ta;

figure,subplot(2,1,1),plot([0,b1],[1,1],'LineWidth',2.5);
hold on;
plot([b1,b],[0,0],'LineWidth',2.5);
axis([0 b+200 0 1.5]);
plot([x,x],[0,1],'LineWidth',2.5)
t=0:0:0;
set(gca,'xtick',t); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',t);
ylabel('Strain ¦Ò','FontSize',12,'FontWeight','bold');

subplot(2,1,2),plot(response,'LineWidth',2.5); hold on;
plot([x,x],[0,C],'--r','LineWidth',2);
axis([0 b+200 0 1]);
text(7000*ta,0.05,'Strain Removed','FontSize',12);
text(4000*ta,0.6, 'Creep Response','FontSize',12,'FontWeight','bold');
text(13500*ta,0.2,'Recovery Response','FontSize',12,'FontWeight','bold')
t=0:0:0;
set(gca,'xtick',t); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',t); 
ylabel('Stress ¦Å','FontSize',12,'FontWeight','bold');



 
