clc;
clear;
 
dt=0.1;
t=0:dt:1000;
eps(1) = 0;
epsdot(1) = 0;
sigma1(1) = 0;
sigma2(1) = 0;
sigmadot(1) = 0;
eps = zeros(size(t));
sigma = zeros(size(t));
sigma1 = zeros(size(t));
sigma2 = zeros(size(t));
sigma3 = zeros(size(t));
sigmaspring = zeros(size(t));
sigmadot1 = zeros(size(t));
sigmadot2 = zeros(size(t));
sigmadot3 = zeros(size(t));
epsdot = zeros(size(t));
 
maxstrain = 0.2;
strainrate = 0.00333;
eta1 = 1160;
eta2 = 14000;
eta3 = 150000;
E = 100;
Espring = 50;

alpha = 0.5;
tau1 = (alpha*eta1)/((1-alpha)*E);
tau2 = (alpha*eta2)/((1-alpha)*E);
tau3 = (alpha*eta3)/((1-alpha)*E);
 
for i = 2:length(t);
    
    eps(i) = eps(i-1)+ strainrate * dt;
 
    if eps(i) > maxstrain;
        eps(i) = maxstrain;
    end;
    
    epsdot(i) = (eps(i)-eps(i-1))/dt;

    if tau1 <= 0;
        sigmadot1(i) = 0;
        sigma1(i) = 0;
        
    else
        sigmadot1(i) = (- sigma1(i-1) + eta1 * epsdot(i) ) / tau1;
        sigma1(i) = sigma1(i-1) + sigmadot1(i) * dt;
    end;
    
     if tau2 <= 0;
        sigmadot2(i) = 0;
        sigma2(i) = 0;
        
    else
        sigmadot2(i) = (- sigma2(i-1) + eta2 * epsdot(i) ) / tau1;
        sigma2(i) = sigma2(i-1) + sigmadot1(i) * dt;
    end;
    
    if tau3 <= 0;
        sigmadot3(i) = 0;
        sigma3(i) = 0;
        
    else
        sigmadot3(i) = (- sigma3(i-1) + eta3 * epsdot(i) ) / tau3;
        sigma3(i) = sigma3(i-1) + sigmadot3(i) * dt;
    end;
    
    sigmaspring(i) = Espring * eps(i);

    sigma(i) = sigma1(i) +  sigma2(i) + sigma3(i) + sigmaspring(i);
    
end;

figure,subplot(212); plot(t,sigma,'LineWidth',2.5); 
axis([0 1200 0 45]);
z=0:0:0;
set(gca,'xtick',z); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',z); 
ylabel('Strain ¦Ò','FontSize',12,'FontWeight','bold');

subplot(211); plot(t,eps,'LineWidth',2.5);
axis([0 1200 0 0.25]);
z=0:0:0;
set(gca,'xtick',z); 
xlabel('Time t','FontSize',12,'FontWeight','bold');
set(gca,'ytick',z); 
ylabel('Stress ¦Å','FontSize',12,'FontWeight','bold');
