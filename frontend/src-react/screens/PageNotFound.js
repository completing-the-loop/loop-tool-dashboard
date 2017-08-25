import React from 'react';
import styles from './PageNotFound.scss';

export default function PageNotFound() {
    return (
        <div className={styles.notFound}>
            <h2>404 - Page Not Found</h2>
            <div>
                <p>
                    You have no routes defined yet and so the catch all route
                    is used to display a 404 page (see PageNotFound.js). Update
                    src/routes.js to include more routes.
                </p>
                <p>
                    TODO: Remove this message :)
                </p>
            </div>
        </div>
    );
}
