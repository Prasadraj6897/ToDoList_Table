// import {increment_reducer} from "./action_reducer_folder/increment_reducer"
// import {decrement_reducer} from "./action_reducer_folder/decrement_reducer"
// import {Product_reducer} from "./action_reducer_folder/Product_ac_red_folder/reducer"
// import {Contact_reducer} from "./action_reducer_folder/contactAppFolder/reducer.contact"
import { combineReducers } from 'redux';
import {Table_reducer} from "./action_reducer_folder/TableAppFolder/reducer.table"
import {User_reducer} from "./action_reducer_folder/TableAppFolder/reducer.user"



let RootReducers = combineReducers(
                                    {
                                        // Product_root_reducer : Product_reducer,
                                        // Contact_root_reducer : Contact_reducer
                                        Table_root_reducer : Table_reducer,
                                       User_root_reducer :User_reducer
                                    }
                                    
                                )

export {RootReducers};