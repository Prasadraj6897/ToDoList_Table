import {RootReducers} from "./root_reducer"

import {createStore, applyMiddleware} from "redux"
import {composeWithDevTools} from "redux-devtools-extension"
import thunk from "redux-thunk"
import {logger} from "redux-logger"

let middleware = [logger, thunk]

let store = createStore(RootReducers, composeWithDevTools(applyMiddleware(...middleware)))

export {store};