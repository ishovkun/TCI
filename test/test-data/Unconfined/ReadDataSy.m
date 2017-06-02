
for i=1:78;
   filename = ['_',num2str(i),'Sy.TRC'];
   M=dlmread(filename,'\t',2,0);
   BigM(:,i+1) = M(:,2); 
end

 BigM(:,1) = M(:,1); 

 for i=1:78;
    plot(BigM(:,1) , BigM(:,i+1)-2*(i-1),'LineWidth',2)
    title('Stress Dependence of Shear Wave (Y) Velocity (Unconfined)')
xlabel('Oscilloscope Time')
ylabel('Real Time') 
ylim([-165 10])
  set(gca,'XtickLabel',[],'YtickLabel',[]);
hold on; 
 end
    