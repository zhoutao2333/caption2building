#include<iostream>
#include<vector>
using namespace std;

const int N = 10;

vector<bool> st(N);
vector<int> res;
int n;

void Prin(int i){
    if(res.size() == n){
        for(int j = 1; j <= n; j++){
            cout<<res[j]<<" ";
        }
        cout<<endl;
        return;
    }
    res.push_back(i);
    st[i] = true;
    for(int j = 1; j <= n; j++){
        if(st[j] == false){
            res.push_back(j);
            st[j] = true;
        }
    }
    Prin(i+1);
    res.pop_back(i);
    st[i] = false;


    
    

}


int main(){
    cin>>n;
    Prin(1);
    
    return 0;
}