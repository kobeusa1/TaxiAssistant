%% read data
tb=readtable('taxi.csv');
tb.time=datetime(tb.time,'InputFormat','H:mm','Format','preserveinput');
%% draw figures
timelist=unique(tb.time);
clear('M');M(length(timelist)) = struct();
figure('Position',[1 1 1024 250]);
i=1;
for k = timelist'
    data=tb(k==tb.time,:);
    subplot(1,2,2)
    myhist(data.longitude,data.latitude,data.pred_pickups,[],[],1);
    c=colorbar;    c.Label.String = 'Number of Taxi Trips';
    %dim = [0.7 0.55 0.3 0.3];
    dim = [0.8 0.7 0.3 0.3];
    annotation('textbox',dim,'String',['Time: ',datestr(k,'HH:MM')],'FitBoxToText','on');
    xlim([  -74.0993,-73.6022]);ylim([40.5128,  41.0964]);
    subplot(1,2,1)
    data.pickups=fillmissing(data.pickups,'constant',0);
    myhist(data.longitude,data.latitude,data.pickups,[],[],1);
    %title('Acutual Number of  NYC Taxi Trips','FontSize',14);
    title('Acutual Heat','FontSize',14);
    zlabel('Acutual Hourly Taxi Trips','FontSize',13);
    xlim([  -74.0993,-73.6022]);ylim([40.5128,  41.0964]);
    c=colorbar;
    c.Label.String = 'Number of Taxi Trips';
    %dim = [0.25 0.55 0.3 0.3];
    dim = [0.35 0.7 0.3 0.3];
    annotation('textbox',dim,'String',['Time: ',datestr(k,'HH:MM')],'FitBoxToText','on');
    drawnow;     
    im{i} = frame2im(getframe(gcf));
    i=i+1;
    clf;
end
%% output gif
filename = 'heat2.gif'; % Specify the output file name
for i = 1:length( im)
    [A,map] = rgb2ind(im{i},256);
    if i == 1
        imwrite(A,map,filename,'gif','LoopCount',Inf,'DelayTime',0.2);
    else
        imwrite(A,map,filename,'gif','WriteMode','append','DelayTime',0.2);
    end
   
end
