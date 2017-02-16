%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Author:       Max
% Date:         16.02.2017
% File:         rfexpPlotter.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Settings
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	rmDir = '/home/pi/mySpecScan/';
	rmFile = 'test.csv';
	lcFile = './samples/';
	ip = '192.168.1.136';
	user = 'pi';
	fstart = 2400;		% in MHz
	fstop = 2500;		% in MHz

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Remember! If this script shall work you have to set up a 
% a ssh key on the machine which is running this script. This
% can be done with:
% ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N pwforkeyencr
% The next step is to install the key on the RPI:
% ssh-copy-id -i ~/.ssh/id_rsa.pub ahmet@myserver 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Get samples
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	cpcmd = ["scp " user "@" ip ":" rmDir rmFile " " lcFile]
	if exist(lcFile, 'dir') ~= 7;
		system(["mkdir " lcFile]);
	end
	system(cpcmd); 
	D = dlmread([ lcFile rmFile]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Process samples
% The rfexplorer is somehow messing it up with the samples,
% so there has to be some post processing.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	i=1;
	while(i <= length(D(:,1)))
		% Is freq. bin out of band?
		% Yes -> bin is crap.
		if( (D(i,1) <= fstart) || (D(i,1) >= fstop) )
			D(i,:) = [];
		end 
		i++;
	end	
	D=sortrows(D,1);
	

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot samples
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	
	fig = figure(1);
	plot(D(:,1),D(:,2));
