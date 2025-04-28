#include <iostream>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <utility>
#include <queue>

#define NUM_STOCKS 488

typedef std::pair<int, int> pr;

// i is leader, j is lagger
double matrix[NUM_STOCKS][NUM_STOCKS];
std::unordered_map<int, std::string> idx_to_ticker;

class Stock{
    public:
    std::vector<float> returns;
    Stock(){
        returns.reserve(2518);
    }
};

class obj{
    public:
    pr idxes;
    double val;
    obj(pr p, double i): idxes(p), val(i) {}
};

class Compare{
    public:
    bool operator()(const obj &o1, const obj &o2){
        return o1.val < o2.val;
    }

};

Stock stock_returns[NUM_STOCKS];

void parseCSV(const std::string& filename, const int &stock_idx) {
    std::ifstream file(filename);
    std::string line;

    // first 5 characters are data/, also don't want to include .csv so we just chare about characters that aren't those 9
    std::string ticker = filename.substr(5, (filename.size() - 9));
    std::cout<<"ticker: "<<ticker<<"\n";

    idx_to_ticker[stock_idx] = ticker;

    Stock &stock = stock_returns[stock_idx];

    // int i = 0;

    // ignore header
    std::getline(file, line);

    // get first close
    std::getline(file, line);
    std::stringstream first(line);
    std::string temp;
    std::vector<std::string> first_row;
    while (std::getline(first, temp, ',')) {
        first_row.push_back(temp);
    }
    double prev_close = stof(first_row[4]);

    // std::cout << "Parsing: " << filename << "\n";
    while (std::getline(file, line)) {
        // ++i;
        std::stringstream ss(line);
        std::string cell;
        std::vector<std::string> row;

        while (std::getline(ss, cell, ',')) {
            row.push_back(cell);
        }

        float new_close = stof(row[4]);
        stock.returns.push_back((new_close - prev_close) / prev_close);
    }
}

int main() {
    // initialize matrix to be 0
    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            matrix[i][j] = 0.0;
        }
    }
    // parse each csv file
    std::string dir_path = "data";
    int idx = 0;
    std::cout<<"begining parsing\n";
    for (const auto& entry : std::filesystem::directory_iterator(dir_path)) {
        if (entry.is_regular_file() && entry.path().extension() == ".csv") {
            parseCSV(entry.path().string(), idx);
            idx++;
        }
    }
    std::cout<<"done parsing\n";
    const float delta = 0.3;

    std::priority_queue<obj, std::vector<obj>, Compare> pq;

    // compute matrix calculations
    // i is leader, j is lagger
    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            if(i == j) continue;
            Stock &leader = stock_returns[i];
            Stock &lagger = stock_returns[j];
            /*
                Monday:     Tuesday:    Wednesday:
                Leader: +5  Leader +3   Leader + 1
                Lagger: 0   Lagger +5   Lagger +3
            
            */
            

            // checking to see if leader @ day = t - 1 before affects lagger @ day = t
            int leader_idx = leader.returns.size() - 2;
            int lagger_idx = lagger.returns.size() - 1;

            // need to iterate backwards because it's from latest days
            while(leader_idx >= 0 && lagger_idx >= 0){


                if(lagger.returns[lagger_idx] >= 0){
                    if(((1 + delta) * lagger.returns[lagger_idx] >= leader.returns[leader_idx]) && (((1 - delta) * (lagger.returns[lagger_idx])) <= leader.returns[leader_idx])){
                        // double temp = (double)std::min(abs(lagger.returns[lagger_idx]), abs(leader.returns[leader_idx])) / (double)std::max(abs(lagger.returns[lagger_idx]), abs(leader.returns[leader_idx]));
                        double temp = lagger.returns[lagger_idx] / leader.returns[leader_idx];
                        matrix[i][j] += (temp * temp);
                        // matrix[i][j]++;
                    }
                }
                else{
                    if(((1 + delta) * lagger.returns[lagger_idx] <= leader.returns[leader_idx]) && (((1 - delta) * (lagger.returns[lagger_idx])) >= leader.returns[leader_idx])){
                        // double temp = (double)std::min(abs(lagger.returns[lagger_idx]), abs(leader.returns[leader_idx])) / (double)std::max(abs(lagger.returns[lagger_idx]), abs(leader.returns[leader_idx]));
                        double temp = abs(lagger.returns[lagger_idx]) / abs(leader.returns[leader_idx]);
                        matrix[i][j] += (temp * temp);
                        // matrix[i][j]++;
                    }
                }

                
                lagger_idx--;
                leader_idx--;
            }
        }
    }

    int adj_matrix[NUM_STOCKS][NUM_STOCKS];

    const int LEAD_LAG_THRESHOLD = 1000;

    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            if(i == j) continue;
            if(matrix[i][j] > LEAD_LAG_THRESHOLD){
                // this is considered an exhibited lead-lag relationship
                adj_matrix[i][j] = 1;
            }
        }
    }

    // initialize to 0
    int out_degree_scores[NUM_STOCKS];
    for(int i = 0; i < NUM_STOCKS; ++i) out_degree_scores[i] = 0;

    // now i is the lagger
    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            if(adj_matrix[j][i] == 1){
                out_degree_scores[i]++;
            }
        }
    }

    const double out_degree_penalty = 0.45;


    // initialize to 0
    int in_degree_scores[NUM_STOCKS];
    for(int i = 0; i < NUM_STOCKS; ++i) in_degree_scores[i] = 0;

    // now i is the leader
    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            if(adj_matrix[i][j] == 1){
                in_degree_scores[i]++;
            }
        }
    }

    const double in_degree_penalty = 0.15;




    for(int i = 0; i < NUM_STOCKS; ++i){
        for(int j = 0; j < NUM_STOCKS; ++j){
            if(i == j) continue;
            matrix[i][j] = matrix[i][j] / (double)(1 + out_degree_penalty * out_degree_scores[j] * in_degree_penalty * in_degree_scores[i]);
            pq.push(obj({i, j}, matrix[i][j]));
            // std::cout << "Leader: " << i << ", lagger: " << j << ", val: " << matrix[i][j] << "\n";
        }
    }

    
    std::string filename = "selected_pairs.txt";
    std::ofstream outfile(filename);

    if (!outfile.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        return 1;
    }

    for(int i = 0; i < 10; ++i){
        auto temp = pq.top();
        pq.pop();
        std::string leader = idx_to_ticker[temp.idxes.first];
        std::string lagger = idx_to_ticker[temp.idxes.second];

        std::cout << "Leader: " << leader << ", lagger: " << lagger << ", val: " << temp.val << "\n";
        outfile << leader << " " << lagger << "\n";
    }

    outfile.close();


    return 0;
}