/**
 * Helper to reduce multiple reducers to a single reducer
 * @param {...Array|Function} reducersConfig either a reducer function or an array of size 2;
 * first element being a path and the second a reducer function. The reducer will be passed the
 * state slice under the specified path. Path can be a single key (eg. 'item') or an array path,
 * (eg. ['entities', 'products'])
 * @returns Function
 */
export default function reduceReducers(...reducersConfig) {
    return (currentState, action) =>
        reducersConfig.reduce(
            (state, config) => {
                if (Array.isArray(config)) {
                    if (config.length !== 2) {
                        throw new Error(
                            'Array parameter to reduceReducers should contain exactly 2 ' +
                            'elements; [key: String|Array<String>, reducer: Function]');
                    }
                    const [key, reducer] = config;
                    const path = Array.isArray(key) ? key : [key];
                    const current = state.getIn(path);
                    const nextState = reducer(current, action);
                    if (current === nextState) {
                        // If nothing has changed don't return a new state object which would
                        // force re-render
                        return state;
                    }
                    return state.setIn(path, nextState);
                }
                const reducer = config;
                return reducer(state, action);
            },
            currentState
        );
}
