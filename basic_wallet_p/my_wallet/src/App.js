import React, { Component } from 'react';
import './App.css';

import axios from 'axios';

class App extends Component {
    constructor() {
        super();

        this.state = {
            id: 'sammy-chang',
            current_balance: -1,
            transactions: []
        };
    }

    componentDidMount = () => {
        this.getWallet();
    };

    getWallet = () => {
        console.log('getting wallet...')
        axios
            .get(`http://localhost:5000/transactions/id/${this.state.id}`)
            .then(res => {
                console.log('res')
                this.setState({
                    transactions: res.data.transactions,
                    current_balance: res.data.current_balance,
                });
            })
            .catch(err => {
                console.log('err')
                console.log(err);
            });
    };

    render() {
        return (
            <div className='App'>
                <header className='App-header'>
                    <h1>Lambda Wallet</h1>
                    <div>
                        {`id: ${this.state.id}`}
                        <br />
                        {`current balance: ${this.state.current_balance} coins`}
                        <br />
                        all transactions: {this.state.transactions.map(transaction => (
                            <div>{JSON.stringify(transaction)}
                            </div>
                        ))}
                    </div>
                </header>
            </div>
        );
    }
}

export default App;
