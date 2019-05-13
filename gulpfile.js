var gulp = require('gulp'),
    sass = require('gulp-sass'),
    //autoprefixer = require('gulp-autoprefixer'),
    //webpack = require('webpack-stream'),
    pump = require('pump');

// Compile the CSS
gulp.task('styles', function(cb) {
    pump([
        gulp.src('styles/theme.scss'),
        sass({
            includePaths: [
                'node_modules/foundation-sites/scss',
                'node_modules'
            ]
        }),
        /*autoprefixer({
            browsers: ['last 2 versions'],
            cascade: false
        }),*/
        gulp.dest('theme/static/css')
    ], cb);
});

//gulp.task('scripts', gulp.series());

// Generic tasks
//gulp.task('default', gulp.parallel('styles', 'scripts'));
gulp.task('default', gulp.parallel('styles'));

gulp.task('watch', gulp.series('default', function(cb) {
    gulp.watch('styles/*.*', gulp.series('styles'));
    //gulp.watch('scripts/**/*.*', gulp.series('scripts'))
    cb();
}));
