import { Record, List, Map, Typed } from 'typed-immutable';
import invariant from 'invariant';
import isPlainObject from 'lodash/isPlainObject';

function isValidStateObject(state) {
    return state instanceof Record || state instanceof List || state instanceof Map;
}

// Helper to get a nice plain text description of a object for debugging
function stateTypeToString(obj) {
    if (isPlainObject(obj)) {
        return 'plain object';
    }
    if (obj && obj.constructor && obj.constructor.prototype[Typed.label]) {
        return obj.constructor.prototype[Typed.label];
    }
    if (obj.constructor.name) {
        return obj.constructor.name;
    }

    if (typeof obj == 'object' && obj.toString) {
        return obj.toString();
    }
    return obj;
}

/**
 * Helper to create a Redux reducer function that enables you to write a
 * reducer that provides an object who's keys are the actions it knows how to
 * handle. If key isn't handled it returns current state.
 *
 * Also checks returned state is immutable and handles converting plain JS
 * object state into immutable instance.
 * @param {Record} stateConstructor this should be a typed-immutable Record.
 * It can optionally be null if you are attaching a reducer to state object
 * defined by another reducer. For example,
 * {
 *   items: {
 *     products: [],
 *   }
 * }
 * If you had an itemsReducer() that defined the structure of 'items' but wanted
 * to attach another reducer on the 'products' keys then you could set the
 * constructor parameter to null
 * @param {Object} handlers each key is an action constant, value the handler function, eg
 *
 * {
 *    // Defines handler for LOGIN
 *    [ActionTypes.LOGIN](state, action) {
 *      return state.update(....);
 *    }
 * }
 */
export default function createReducer(constructor, handlers, transformInitialState = data => data) {
    let validStateConstructor = constructor;
    return (state = null, action) => {
        if (validStateConstructor == null) {
            // When constructor is passed as null it is assumed the reducer is
            // attached to a state structure defined by another reducer. In this
            // cases store the type constructor we expect all returned types to
            // be so we can validate it below.
            validStateConstructor = state.constructor;
        }

        const handler = handlers[action.type];
        let currentState = state;
        if (state == null) {
            invariant(constructor, 'You must provide a constructor if this is a reducer ' +
                                   'that defines the state shape');
            // Provide initial state
            currentState = new constructor();
            invariant(isValidStateObject(currentState),
                      'Initial state for a reducer must be an typed-immutable Record.');
        }

        if (!isValidStateObject(currentState)) {
            invariant(constructor, 'You must provide a constructor if this is a reducer ' +
                                   'that defines the state shape');
            // This handles initial data passed to configureStore() as a plain JS object. This is
            // useful for populating client side data from the server. See main.js for how this
            // is handled (window.__INITIAL_STATE__)
            currentState = new constructor(transformInitialState(currentState));
        }

        if (!handler) {
            return currentState;
        }

        const nextState = handler(currentState, action);

        invariant(
            nextState != null,
            `Reducer returned ${nextState}. Did you forget to return for action '${action.type}'?`
        );
        if (!(nextState instanceof validStateConstructor)) {
            invariant(
                nextState instanceof validStateConstructor,
                'Reducers must return instance of provided stateConstructor. Using immutable ' +
                'make sure you are returning the root state object for where your reducer is ' +
                'attached and not some child descendant or other value. \n\n' +
                "eg. if you have a child called 'items' which is a list then doing this: \n\n" +
                '  return state.items.push(5)\n\n' +
                'will return a new list with 5 pushed on rather than a new instance of your ' +
                "state with new value appended to 'items'. What you want is: \n\n" +
                '  return state.update(items, items => items.push(5));\n\n' +
                'We expected an instance of ' +
                `${(validStateConstructor.prototype[Typed.label] || validStateConstructor.name)} ` +
                `but instead got ${stateTypeToString(nextState)}`
            );
        }

        return nextState;
    };
}
