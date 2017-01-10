#include <bits/stdc++.h>
using namespace std;
#define ll long long
#define n 10000
#define m 1000

ll getRand(ll l,ll r){
    return l+rand()%(r-l+1);
}

ll newPos(){
    ll arr[]={1,97,1001,1979,10000,8989};
    ll x=rand()%6;
    return arr[x];
}

int main(){
    ll myPos=1,wasHit,l=1,r=n,iters=0,prevPos;//iters denote no of iterations in binary search
    ll seaEagles=10;
    ll agni=1;
    char posDiff;
    ll instantTrans=5;
    ll hitPos=(l+r)/2;
    cout<<myPos<<endl;
    prevPos=myPos;
    fflush(stdout);
    ll i,j;
    for(i=1;i<=m;i++){
        if(i==1){
            cin>>wasHit;//will be 0 initially
            cout<<0<<endl<<hitPos<<" "<<"xFalcon"<<endl;//no change in own position , hit enemy with falcon
            fflush(stdout);
        }	
        else{
            cin>>wasHit>>posDiff;
            if(wasHit==1){//change your pos
                myPos=newPos();
                prevPos=myPos;
            }
            else{//may or may not use instant transmission
                if(instantTrans>=1 && i%200==0){
                    myPos=getRand(max((ll)1,prevPos-50),min((ll)n,prevPos+50));
                    instantTrans--;
                }
                else
                {
                    myPos=0;
                }      
            } 
            cout<<myPos<<endl;
            if(posDiff=='+'){
                iters++;
                l=hitPos;
                hitPos=(l+r)/2;
            }
            else if(posDiff=='-'){
                iters++;
                r=hitPos; 
                hitPos=(l+r)/2; 
            }
            if(iters>15 || posDiff=='0'){
                iters=0;
                l=1;
                r=n;
                hitPos=(l+r)/2;
            }
            if(r-l<=2 && agni>=1){
                cout<<hitPos<<" "<<"xAgni-V"<<endl;
                agni--;
            }
             else
                cout<<hitPos<<" "<<"xFalcon"<<endl;
            fflush(stdout);
        }

    }
    return 0;
}
