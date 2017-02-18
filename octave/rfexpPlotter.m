%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Author:       S3xm3x
% Date:         16.02.2017
% File:         rfexpPlotter.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function rfexpPlotter(fstart,fstop,steps,lat,long)
	
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Settings
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		rmDir = '/home/pi/specScanner/';
		script = 'specScanner.py'
		rmFile = 'temp.csv';
		ip = '192.168.43.130';
		user = 'pi';
		
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Remember! If this script shall work you have to set up a 
	% a ssh key on the machine which is running this script. This
	% can be done with:
	% ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N pwforkeyencr
	% The next step is to install the key on the RPI:
	% ssh-copy-id -i ~/.ssh/id_rsa.pub ahmet@myserver 
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Create and transfer samples
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		crcmd = ['ssh ' user '@' ip ' ''sudo python3.5 ' rmDir script ' -a '  num2str(fstart) ' -b ' num2str(fstop) ' -s ' num2str(steps) ' '''];
		system(crcmd);				
		sampFolder = strftime ('%Y_%m_%d_%H_%M_%S', localtime (time ()));
		if exist(['samples_' sampFolder]', 'dir') ~= 7;
                        system(['mkdir ' 'samples_' sampFolder] );
                end
		cpcmd = ['scp ' user '@' ip ':' rmDir rmFile ' ' 'samples_' sampFolder];              
		system(cpcmd); 
		P = [];
		P = dlmread([ 'samples_' sampFolder '/' rmFile])

	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Process samples
	% The rfexplorer is somehow messing it up with the samples,
	% so there has to be some post processing.
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		%i=1;
		%while(i <= length(P(:,1)))
			% Is freq. bin out of band?
			% Yes -> bin is crap.
		%	if( (P(i,1) <= fstart) || (P(i,1) >= fstop) )
		%		P(i,:) = [];
		%	end 
		%	i++;
		%end	
		%P = sortrows(P,1);
		

	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	% Plot samples
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		fig = figure(1);				% actual plot
		plot(P(:,1),P(:,2));

		title([ 'Spectrum Analysis from ' num2str(fstart) ' MHz to ' num2str(fstop) ' MHz']);
		xlabel('f/Hz');
		ylabel('|P| in dBm');

		Pmax = max(P(:,2));				% axis
		Pmin = min(P(:,2));
		axis([fstart fstop Pmin 0.9*Pmax]);
		
		set(gca,'xtick',fstart:(fstop-fstart)/20:fstop);% grid
		set(gca,'ytick',round(Pmin/10)*10:5:round((0.9*Pmax)/10)*10);
		grid on;
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Save configuration
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

                dlmwrite(['samples_' sampFolder '/conf.csv'], [fstart,fstop,steps,lat,long]);
endfunction;
