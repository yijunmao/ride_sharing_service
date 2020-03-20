# erss-hwk1-ym134-yl561

Django Web-App: Ride Sharing Service
## Homepage
<p>Our homepage is a direct user sign-in page, which the log-in window is in the middle of the main webpage area right under the navagation bar.</p> 

<p>If you are a new user for our Ride Sharing Application, you could either click the 'register' button on the very right of the navigation bar or click the sign up link on the bottom of the log-in window.</p>

##  Registration
<p>If you get linked to the regestation page, all you need to fill in is your username which later will be used for logging in, your real name, and your email address. After your finishing regestration, you will be redirect to the homepage to sign in.</p> 

## User's Home Page
<p>After you obtain your account, you are now inside the core of this web app. The three huge block are the main functions: Request a Ride, Share a Ride, Drive a Ride.</p> 

<p>On the left side of this page, you would see three additions links. The first one "be a driver" is a driver regestration link. The second one 'rides history' lists all your completed rides. The last one "active rides" presents you all the ongoing rides you involve in no matter what role your are. You can notice that the navagation bar now has an addtional link which helps you sign out from your user's home </p> 

#### Request A Ride
<p>Click the blue button on the first Jumbotron prompts you to the ride requesting page. You are supposed to enter your destination, arrival time, number of passengers from your party, sharable status, Maximum allowd sharers in your ride, prefered vehicle type and special request. Most of the fields are actully directly required in the homework instructions. We add an extra feature when you are requesting a ride which the maximum allowed sharers. The reason is that if numerous sharers keep adding to your ride, the total number of passengers in that ride would grow without end. In such case, there wil be no fit vehicle that was able to take over that ride. More details will be discussed later.</p>

#### Share A Ride
<p>User can share a existing ride by entering the destination, acceptable arrival time window and party size. You must fill in all four fields so see any sharable rides. Only the destination is fully matched can a sharer join that specific ride. Besides, the system would automatically filter the rides that the arrival time is outside your acceptable window.</p>

<p>Once a ride is found, it will be listed  on the table below. And you could easily join that ride by clicking the join button. One thing need to be noticed that, when you click the join button, the system will compute the number of total sharers in that ride at current time, if your party size exceeds the remaining space on that ride (which is maximum allowed - No.existing sharers) you will be rejected to join this ride!</p>

#### As A Driver
<p>If you have not registered as a driver yet, you are not allowed to see the driver menu page. An error message would pop up to tell you become a driver first. Suppose you are already a driver now, when you click the 'driver' button on the last Jumbotron, you would get into the driver menu.</p>

<p>At the top of that page, there are three searching criteria for drivers to search rides based on their preferences. The driver can specify the exact place they want to go to see if any rides happen to have the same destination. Driver could also search the open rides that within a specific time interval by entering the earliest time and latest time. All three fields are optional for drivers. If they do not specify anything, they would see a list of open rides which fit their vehicle capacity, vehicle type and match the speical request by hidden filtering. They do not need to fill all three search fields in this web. For instance, if you only enter the earliest time area, the table below would erase out the rides which have earlier arrvial time they you want. Same thing for destintion and lastest time.</p>

<p>After you find a ride you are interested in, you could simply click the 'take' button to drive this ride for the owners and sharers. You could take as many rides as you wish. We do not set any limitations for driver. Taking the rides with the same arrival time is also allowed but most likely the driver would not be able to finish all of them but the driver himself should take the blame. A clear mind person would not do that unless you are expecting the complaints from customers. </p>

<p>In the driver's menu, the navigation bar provides another link which allows the driver to see their profiles. Basically, anything he provides in the registration phase would be shown there. Drivers are allowed to edit their profile when there are no confirmed rides by that driver. Suppose you enter a wrong number of vehicle capacity, or a wrong car type during your driver registration, and you want to change them in your profile, which is totally reasonable. However, if you do not notice that in the first place and you have confirmed a ride to drive already, then you are in trouble. Ride owners would get notified by email at that time and they are expecting your arrival. You could not change your vehicle capacity to a number which is smaller than total number of passengers on that ride. You could not change the car type which does not fit ride owner's request as well.</p>

<p>Friendly Reminder: Borrow a car that fits the entities you provides during the registration, complete the rides and then change your profile. Or Buy a new car.</p>


#### Be A Driver
<p>If you want to be a driver, you need to register first! Most of the info you need enter is related to vehicle. Any rides with speical info should match the vehicle speical info for the driver to see the that ride. Everything else is registration routine.</p>

#### Active Rides
<p>In active rides, you are able to see all the ongoing (open and confirmed) rides you are invovled. You have three tables right there. The first table shows all the uncompleted
rides you own. You have two links at the end of each table row -- detail and delete. If you click on detail, you will be prompted to the detail page of this ride. You are allowed to see all the info about this ride including sharable status, destination, time, sharers' contact info, and status of this ride. At the bottom of this detail page, 
page, you will find a edit button for you to change your ride request. If that ride is confirmed by a driver, then you are not allowed to change anything. The field 
max_allowed_persons is immutable once you set it down because we do not want any sharers get kicked out of the ride. If you set the ride sharable at first and decide to change it
to unsharable, you would get permission if there's no sharer in your ride currently and maximum allowed person would be automatically set to 0. If not, you will be prevented to alter this field. 
If your ride is unsharable first and you decide to make it sharable, besides checking the corresponding box, you also need to fill in the maximum allowed persons in the next page. 
If there are sharers in your ride already, they will receive emails telling them the modication you make on either destination or time upon submitting the updates.</p>

<p>The next table shows the open and confirmed rides you are sharing. As a sharer, you can view the same rides detail as owners do but you are only allowed to edit the party size of your side if the ride is open. If the updated number makes the total number of passengers exceed the maximum allowed persons, you will be asked to reduce your party size.</p>

<p>The third table is driver's rides list, which shows all your confirmed rides as a driver but of course, you need to be a driver first. For each ride displayed here, we also have two links: detail and edit status. When you click on detail, you can check out everything about this ride. When you click on edit status, you can complete the ride. After doing that, the ride would be removed from current page and moved to ride history.</p>


