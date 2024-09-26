from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
import pandas as pd
import numpy as np

# keys to access the caches
CACHE_ACCOUNTS_KEY = 'accounts'
CACHE_BAD_TRANSACTIONS_KEY = 'bad_transactions'

# reset system to blank state by clearing cache
def reset_cache():
    cache.set(CACHE_ACCOUNTS_KEY, {})
    cache.set(CACHE_BAD_TRANSACTIONS_KEY, [])

# processes user uploaded csv file
def process_transaction_file(file):
    bad_transactions = []
    accounts = cache.get(CACHE_ACCOUNTS_KEY, {})

    # error handler
    try:
        # reads user uploaded file
        # pandas supports a wide range of file types
        # we can cover various file type in the future
        df = pd.read_csv(file, names=['Account Name', 'Card Number', 'Transaction Amount', 
                                      'Transaction Type', 'Description', 'Target Card Number'])
        
        # checks the fields required to fulfill a transaction for null values
        required_fields = ['Account Name', 'Card Number', 'Transaction Amount', 'Transaction Type']
        if df[required_fields].isna().values.any():
            return JsonResponse({'error': 'Missing required values in the uploaded file.'})
        
        # iterate through each transaction record and appropriately process it
        for _,row in df.iterrows():
            # error handler
            try:
                # get the particulars of each transaction
                account_name = row['Account Name']
                card_number = row['Card Number']
                transaction_amount = float(row['Transaction Amount'])
                transaction_type = row['Transaction Type']
                target_card_number = row['Target Card Number']

                # check if account is in cache, if DNE, create account and its cards
                if account_name not in accounts:
                    accounts[account_name] = {}
                
                if card_number not in accounts[account_name]:
                    accounts[account_name][card_number] = 0.0

                # process each type of transaction accordingly
                if transaction_type == 'Credit':
                    accounts[account_name][card_number] += transaction_amount
                elif transaction_type == 'Debit':
                    accounts[account_name][card_number] -= transaction_amount
                elif transaction_type == 'Transfer' and target_card_number:
                    if target_card_number not in accounts[account_name]:
                        accounts[account_name][target_card_number] = 0.0
                    accounts[account_name][card_number] -= transaction_amount
                    accounts[account_name][target_card_number] += transaction_amount
                else:
                    raise ValueError(f'Invalid transaction type: {transaction_type}')

            # error occured, bad transaction                
            except Exception as e:
                # append to bad transaction dict.
                bad_transactions.append({'transaction' : row.to_dict(), 'error': str(e)})
    
    # error with file processing
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
    # cache the created accounts and bad transactions
    cache.set(CACHE_ACCOUNTS_KEY, accounts)
    cache.set(CACHE_BAD_TRANSACTIONS_KEY, cache.get(CACHE_BAD_TRANSACTIONS_KEY, []) + bad_transactions)

    return JsonResponse({'status': 'success', 'bad_transactions': bad_transactions})

def chart_of_accounts(request):
    accounts = cache.get(CACHE_ACCOUNTS_KEY, {})
    data = []

    for account_name, cards in accounts.items():
        for card_number, balance in cards.items():
            data.append({
                'account_name' : account_name,
                'card_number' : card_number,
                'balance' : balance
            })

    return JsonResponse(data, safe=False)

def collections_report(request):
    accounts = cache.get(CACHE_ACCOUNTS_KEY, {})
    data = []

    for account_name, cards in accounts.items():
        for card_number, balance in cards.items():
            if balance < 0:
                data.append({
                    'account_name' : account_name,
                    'card_number' : card_number,
                    'balance' : balance
                })

    return JsonResponse(data, safe=False)

def bad_transactions_report(request);
    bad_transactions = cache.get(CACHE_BAD_TRANSACTIONS_KEY, [])
    return JsonResponse(bad_transactions,, safe=False)

def reset_system(request):
    reset_cache()
    return JsonResponse({'status' : 'system reset'})